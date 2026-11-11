"""Stage 12 (phase 3): improve the ratings using held-out predictive validity.

Yardstick. Rate players from one random half of the matches, then score how well that rating predicts
the same players' raw pressure performance in the OTHER half (weighted Spearman, weights = pressure
balls in the held-out half), averaged over many splits, in both directions. Unlike rating-versus-rating
correlation this does not reward a score for being stable noise. Two targets: pressure NRAE per 100 balls
and pressure WPA per 100 balls.

Every candidate is a way of turning the same ball-level credit table into a score. Nothing here looks at
player names. Output: outputs/tables/phase3_candidates.csv
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import json

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from common import CFG, INTERIM, PROCESSED, SEED, save_table
from ratings_lib import Prep, rate, composite, COMPONENTS
from robust_lib import random_splits


def wspearman(a, b, w):
    ra, rb = rankdata(a), rankdata(b)
    w = w / w.sum()
    ma, mb = (w * ra).sum(), (w * rb).sum()
    c = (w * (ra - ma) * (rb - mb)).sum()
    return c / np.sqrt((w * (ra - ma) ** 2).sum() * (w * (rb - mb) ** 2).sum())


def target(df, role, part_ids, pcol="pA"):
    d = df[df.match_id.isin(part_ids) & df[pcol].astype(bool)]
    unit = d.faced if role == "bat" else pd.Series(1.0, index=d.index)
    g = pd.DataFrame({"player_id": d.player_id, "unit": unit * d.w_comp, "nrae": d.nrae * d.w_comp,
                      "wpa": d.wpa * d.w_comp}).groupby("player_id").sum()
    g["nrae100"] = 100 * g.nrae / g.unit
    g["wpa100"] = 100 * g.wpa / g.unit
    return g[g.unit >= 20]


def scorers(prep, lam, lam_alt):
    """name -> Series(player_id -> score) among players eligible at half scale."""
    el = prep.eligible(0.5, require_recent=False)
    comp = rate(prep, *lam)
    out = {}
    t = composite(comp, el, weights=CFG["composite_weights_spec"])
    out["primary composite"] = t.set_index("player_id").rating
    for c, lab in [("level", "level only"), ("normal", "normal effect only"), ("impact", "impact only"),
                   ("consistency", "consistency only"), ("delta", "delta only"), ("level_eb", "level (empirical Bayes)")]:
        out[lab] = comp[el].set_index("player_id")[c]
    base = CFG["composite_weights_spec"]
    for lab, w in [("composite without delta", dict(base, delta=0.0)), ("composite without consistency", dict(base, consistency=0.0)),
                   ("composite without delta and consistency", dict(base, delta=0.0, consistency=0.0)),
                   ("level 0.6 impact 0.4", dict(level=0.6, impact=0.4, consistency=0.0, delta=0.0)),
                   ("level 0.8 impact 0.2", dict(level=0.8, impact=0.2, consistency=0.0, delta=0.0))]:
        out[lab] = composite(comp, el, weights=w).set_index("player_id").rating
    # stronger shrinkage of the delta
    comp2 = rate(prep, lam[0], lam_alt)
    out["composite, delta penalty x10"] = composite(comp2, el).set_index("player_id").rating
    return out


def main(n_splits=20):
    print("Stage 12: improvement candidates on held-out predictive validity")
    lam_all = json.load(open(os.path.join(INTERIM, "lambdas.json")))
    rows = []
    for role, fname in [("bat", "bat_credit"), ("bowl", "bowl_credit")]:
        df = pd.read_parquet(os.path.join(PROCESSED, f"{fname}.parquet"))
        lam = (lam_all[role]["lambda_main"], lam_all[role]["lambda_delta"])
        mids = np.sort(df.match_id.unique())
        splits = random_splits(mids, n_splits)
        variants = {"": dict(), "leverage-weighted (alpha 1)": dict(lev_alpha=1.0), "leverage-weighted (alpha 0.5)": dict(lev_alpha=0.5)}
        acc = {}
        for sp in splits:
            for flip in (False, True):
                a_ids = mids[~sp] if flip else mids[sp]
                b_ids = mids[sp] if flip else mids[~sp]
                tg = target(df, role, b_ids)
                dA = df[df.match_id.isin(a_ids)]
                for vname, kw in variants.items():
                    prep = Prep(dA, role, **dict(dict(lev_alpha=0.0), **kw))
                    sc = scorers(prep, lam, lam[1] * 10) if vname == "" else \
                        {"level only": rate(prep, *lam)[prep.eligible(0.5, require_recent=False)].set_index("player_id").level,
                         "composite": composite(rate(prep, *lam), prep.eligible(0.5, require_recent=False), weights=CFG["composite_weights_spec"]).set_index("player_id").rating}
                    for sname, s in sc.items():
                        name = f"{sname} [{vname}]" if vname else sname
                        common = s.index.intersection(tg.index)
                        if len(common) < 15:
                            continue
                        w = tg.loc[common, "unit"].values
                        acc.setdefault(name, []).append((wspearman(s[common].values, tg.loc[common, "nrae100"].values, w),
                                                         wspearman(s[common].values, tg.loc[common, "wpa100"].values, w), len(common)))
        for name, v in acc.items():
            v = np.array(v)
            rows.append(dict(role=role, candidate=name, n_trials=len(v), mean_players=v[:, 2].mean(),
                             pred_nrae=v[:, 0].mean(), pred_nrae_se=v[:, 0].std() / np.sqrt(len(v)),
                             pred_wpa=v[:, 1].mean(), pred_wpa_se=v[:, 1].std() / np.sqrt(len(v))))
        print(f"  {role} done")
    t = pd.DataFrame(rows)
    save_table(t, "phase3_candidates.csv")
    for role in ("bat", "bowl"):
        print(t[t.role == role].sort_values("pred_nrae", ascending=False)[["candidate", "pred_nrae", "pred_nrae_se", "pred_wpa"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
