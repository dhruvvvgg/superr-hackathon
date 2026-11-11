"""V2 stage A: choose the design options of the rating by how well they predict FUTURE pressure performance,
without fitting noise.

Evidence trials (one trial = fit on training matches, score against held-out pressure performance):
  tuning:        5 rolling windows (train before T, test the next 6 months, T = 2023-04, 2023-10, 2024-04,
                 2024-10, 2025-04) plus 20 random half splits of the matches (seed A, both directions)
  confirmation:  2 later rolling windows (2025-10 to 2026-04, 2026-04 to 2026-11) plus 20 random half splits
                 (seed B). Never used to choose anything.

Adoption rule: start from a stated reference. Move an option away from the reference only if the paired
difference in the objective (mean of the NRAE-target and WPA-target correlations) is more than 2 standard
errors across the tuning trials. Otherwise keep the reference. This is what stops the search from fitting noise.

Output: outputs/v2/search_log.csv, confirm.csv, chosen_config.json
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import json

import numpy as np
import pandas as pd

from common import PROCESSED, ROOT, SEED
from v2_lib import eval_fold, eval_split

OUT = os.path.join(ROOT, "outputs", "v2")
os.makedirs(OUT, exist_ok=True)
ANCHOR = pd.Timestamp("2026-11-01")
TUNE_CUTS = ["2023-04-01", "2023-10-01", "2024-04-01", "2024-10-01", "2025-04-01"]
CONF_CUTS = [("2025-10-01", 6), ("2026-04-01", 7)]
REFERENCE = dict(half_life=24.0, alpha=1.0, assoc_w=0.5, lam=3000.0, role_prior=False, opp_adjust=True)
GRID = [("lam", [300.0, 1000.0, 3000.0, 10000.0, 30000.0]), ("alpha", [0.0, 0.5, 1.0, 1.5, 2.0]),
        ("half_life", [6.0, 12.0, 24.0, 48.0, None]), ("assoc_w", [0.25, 0.5, 1.0]),
        ("role_prior", [True, False]), ("opp_adjust", [True, False])]
SCORES = ["nrae", "wpa", "blend0.25", "blend0.5", "blend1"]


def raw_scores(tr, role, st):
    d = tr[tr.pA.astype(bool)]
    out = {"raw NRAE": st.nrae100.where(st.unit >= 30)}
    if role == "bat":
        g = d[d.faced == 1].groupby("player_id").agg(r=("runs", "sum"), b=("runs", "size"))
        out["raw strike rate"] = 100 * g.r / g.b
    else:
        g = d.groupby("player_id").agg(r=("bowler_runs", "sum"), b=("bowler_runs", "size"))
        out["raw economy (negated)"] = -6 * g.r / g.b
    return out


def split_sets(mids, n, seed):
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        perm = rng.permutation(len(mids))
        a = set(mids[perm[: len(mids) // 2]])
        b = set(mids) - a
        out += [a, b]
    return out


def trials(df, role, cfg, kind, extra=None):
    """list of result dicts. kind: 'tune' or 'conf'."""
    mids = np.sort(df.match_id.unique())
    res = []
    if kind == "tune":
        for c in TUNE_CUTS:
            res.append(eval_fold(df, role, c, 6, cfg, extra_scores=extra, min_test=20))
        for s in split_sets(mids, 10, SEED + 11):
            res.append(eval_split(df, role, s, cfg, ANCHOR, extra_scores=extra))
    else:
        for c, m in CONF_CUTS:
            res.append(eval_fold(df, role, c, m, cfg, extra_scores=extra, min_test=20))
        for s in split_sets(mids, 10, SEED + 29):
            res.append(eval_split(df, role, s, cfg, ANCHOR, extra_scores=extra))
    return res


def vec(res, score="nrae"):
    return np.array([0.5 * (r[score][0] + r[score][1]) for r in res])


def main():
    print("V2 stage A: search with a 2-standard-error adoption rule")
    data = {r: pd.read_parquet(os.path.join(PROCESSED, f)) for r, f in [("bat", "bat_credit.parquet"), ("bowl", "bowl_credit.parquet")]}
    log, chosen = [], {}
    for role, df in data.items():
        cfg = dict(REFERENCE)
        ref_vec = vec(trials(df, role, cfg, "tune"))
        for key, values in GRID:
            cur = ref_vec
            best = (None, cfg[key], 0.0)
            for v in values:
                if v == cfg[key]:
                    continue
                vv = vec(trials(df, role, dict(cfg, **{key: v}), "tune"))
                d = vv - ref_vec
                m, se = float(np.nanmean(d)), float(np.nanstd(d) / np.sqrt(np.sum(~np.isnan(d))))
                log.append(dict(role=role, option=key, value=str(v), reference=str(cfg[key]), objective=float(np.nanmean(vv)),
                                diff_vs_reference=m, se=se, z=m / se if se else np.nan))
                if m > 2 * se and m > best[2]:
                    best = (vv, v, m)
            if best[0] is not None:
                cfg[key] = best[1]
                ref_vec = best[0]
                print(f"  {role}: {key} -> {best[1]} (+{best[2]:.4f})", flush=True)
            else:
                print(f"  {role}: {key} stays {cfg[key]}", flush=True)
        # output score variant, same rule against plain NRAE
        res = trials(df, role, cfg, "tune")
        base = vec(res, "nrae")
        score, sbest = "nrae", 0.0
        for sname in SCORES[1:]:
            d = vec(res, sname) - base
            m, se = float(np.nanmean(d)), float(np.nanstd(d) / np.sqrt(np.sum(~np.isnan(d))))
            log.append(dict(role=role, option="score", value=sname, reference="nrae", objective=float(np.nanmean(vec(res, sname))),
                            diff_vs_reference=m, se=se, z=m / se if se else np.nan))
            if m > 2 * se and m > sbest:
                score, sbest = sname, m
        print(f"  {role}: score variant {score}", flush=True)
        chosen[role] = dict(cfg=cfg, score=score)
    json.dump(chosen, open(os.path.join(OUT, "chosen_config.json"), "w"), indent=1, default=str)
    pd.DataFrame(log).to_csv(os.path.join(OUT, "search_log.csv"), index=False, float_format="%.5f")

    rows = []
    for role, df in data.items():
        methods = [("v2 chosen", chosen[role]["cfg"], chosen[role]["score"]), ("reference", REFERENCE, "nrae"),
                   ("unweighted level (alpha 0)", dict(REFERENCE, alpha=0.0), "nrae"),
                   ("almost no shrinkage (lam 30)", dict(REFERENCE, lam=30.0), "nrae")]
        for kind, label in [("tune", "tuning trials"), ("conf", "confirmation trials")]:
            ref_res = None
            for name, cfg, sc in methods:
                res = trials(df, role, cfg, kind, extra=raw_scores if name == "reference" else None)
                v = vec(res, sc)
                if name == "reference":
                    ref_v = v
                rows.append(dict(role=role, method=name, trials=label, score=sc, objective=np.nanmean(v), se=np.nanstd(v) / np.sqrt(len(v)),
                                 corr_nrae_target=np.nanmean([r[sc][0] for r in res]), corr_wpa_target=np.nanmean([r[sc][1] for r in res]),
                                 players=np.mean([r["n"] for r in res])))
                if name == "reference":
                    for b in [k for k in res[0] if k.startswith("raw")]:
                        vb = vec(res, b)
                        rows.append(dict(role=role, method=b, trials=label, score=b, objective=np.nanmean(vb), se=np.nanstd(vb) / np.sqrt(len(vb)),
                                         corr_nrae_target=np.nanmean([r[b][0] for r in res]), corr_wpa_target=np.nanmean([r[b][1] for r in res]),
                                         players=np.mean([r["n"] for r in res])))
    t = pd.DataFrame(rows)
    # paired difference of every method against the reference, per split
    t.to_csv(os.path.join(OUT, "confirm.csv"), index=False, float_format="%.4f")
    pd.set_option("display.width", 220)
    print(t.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
