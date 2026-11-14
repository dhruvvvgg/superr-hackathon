"""V2 stage A: choose rating options using forward-only evidence about FUTURE pressure performance.

Each trial trains only on matches strictly before a cutoff and scores the following six months.
Tuning uses five rolling windows (2023-04 through 2025-04); confirmation uses two later windows
(2025-10 and 2026-04). Random half-sample splits are excluded from model selection because they can
train on future matches relative to the scored matches.

Adoption rule: start from a stated reference. Move an option only if the paired difference in the
mean NRAE-target/WPA-target correlation exceeds two standard errors across the tuning windows.
Confirmation windows are diagnostics only and never choose a configuration.

Outputs include search_log.csv, confirm.csv, validation_audit.csv and chosen_config.json.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import json

import numpy as np
import pandas as pd

from common import PROCESSED, ROOT
from v2_lib import eval_fold, rating_eligible_ids

OUT = os.path.join(ROOT, "outputs", "v2")
os.makedirs(OUT, exist_ok=True)
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


def trials(df, role, cfg, kind, extra=None):
    """Return only chronological forward-window trials; never train on a later match."""
    cuts = [(c, 6) for c in TUNE_CUTS] if kind == "tune" else CONF_CUTS
    return [eval_fold(df, role, c, months, cfg, extra_scores=extra, min_test=20)
            for c, months in cuts]


def temporal_audit(df, role):
    """Auditable dates and match counts for every tuning and confirmation window."""
    dates = pd.to_datetime(df.match_date)
    rows = []
    windows = [("tuning", c, 6) for c in TUNE_CUTS] + [
        ("confirmation", c, months) for c, months in CONF_CUTS
    ]
    for kind, cut_text, months in windows:
        cut = pd.Timestamp(cut_text)
        end = cut + pd.DateOffset(months=months)
        train = dates < cut
        test = (dates >= cut) & (dates < end)
        train_dates, test_dates = dates[train], dates[test]
        if not train.any() or not test.any():
            raise ValueError(f"{role} {kind} window {cut_text} has an empty train or test set")
        future = int(df.loc[train & (dates >= test_dates.min()), "match_id"].nunique())
        if future:
            raise AssertionError(f"{role} {cut_text}: training contains future matches")
        rows.append(dict(role=role, kind=kind, cutoff=cut_text, test_end=end.date().isoformat(),
                         train_matches=int(df.loc[train, "match_id"].nunique()),
                         test_matches=int(df.loc[test, "match_id"].nunique()),
                         eligible_train_players=int(len(rating_eligible_ids(df.loc[train], role, cut))),
                         train_max_date=train_dates.max().date().isoformat(),
                         test_min_date=test_dates.min().date().isoformat(),
                         future_train_matches=future))
    return rows


def vec(res, score="nrae"):
    return np.array([0.5 * (r[score][0] + r[score][1]) for r in res])


def main():
    print("V2 stage A: search with a 2-standard-error adoption rule")
    data = {r: pd.read_parquet(os.path.join(PROCESSED, f)) for r, f in [("bat", "bat_credit.parquet"), ("bowl", "bowl_credit.parquet")]}
    log, chosen, audit_rows = [], {}, []
    for role, df in data.items():
        audit_rows.extend(temporal_audit(df, role))
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
    pd.DataFrame(audit_rows).to_csv(os.path.join(OUT, "validation_audit.csv"), index=False)

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
