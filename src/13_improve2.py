"""Stage 13 (phase 3): focused candidates built on a leverage-weighted level, with paired comparisons
against the current composite and an untouched temporal holdout.

Selection data: 20 random match splits (two directions each), held-out pressure NRAE and WPA per 100
balls. Confirmation data (never used to choose): rate on 2022-2024 matches, predict 2025-2026 pressure
performance. Output: outputs/tables/phase3_final_candidates.csv, phase3_temporal.csv
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import importlib.util
import json

import numpy as np
import pandas as pd

from common import CFG, INTERIM, PROCESSED, save_table
from ratings_lib import Prep, rate, composite
from robust_lib import random_splits

spec = importlib.util.spec_from_file_location("imp", os.path.join(os.path.dirname(__file__), "12_improve.py"))
imp = importlib.util.module_from_spec(spec); spec.loader.exec_module(imp)

W = lambda **k: dict(dict(level=0, impact=0, consistency=0, delta=0), **k)
CANDS = {
    "spec composite (phase 1-2)": ("a0", CFG["composite_weights_spec"]),
    "level (unweighted)": ("a0", W(level=1)),
    "lev-level a=1": ("a1", W(level=1)),
    "lev-level a=2": ("a2", W(level=1)),
    "lev 0.8L 0.2I a=1": ("a1", W(level=.8, impact=.2)),
    "lev 0.7L 0.3I a=1": ("a1", W(level=.7, impact=.3)),
    "lev 0.6L 0.25I 0.15D a=1": ("a1", W(level=.6, impact=.25, delta=.15)),
    "lev spec weights a=1": ("a1", CFG["composite_weights_spec"]),
    "lev 0.7L 0.3I a=2": ("a2", W(level=.7, impact=.3)),
}
ALPHA = {"a0": 0.0, "a1": 1.0, "a2": 2.0}


def scores(dA, role, lam):
    out = {}
    for ak, al in ALPHA.items():
        prep = Prep(dA, role, lev_alpha=al)
        comp = rate(prep, *lam)
        el = prep.eligible(0.5, require_recent=False)
        out[ak] = (comp, el)
    return out


def main(n_splits=20):
    print("Stage 13: focused candidates")
    lam_all = json.load(open(os.path.join(INTERIM, "lambdas.json")))
    rows, trows = [], []
    for role, fname in [("bat", "bat_credit"), ("bowl", "bowl_credit")]:
        df = pd.read_parquet(os.path.join(PROCESSED, f"{fname}.parquet"))
        lam = (lam_all[role]["lambda_main"], lam_all[role]["lambda_delta"])
        mids = np.sort(df.match_id.unique())
        year = df.drop_duplicates("match_id").set_index("match_id").year.reindex(mids).values
        trials = {k: [] for k in CANDS}
        def evaluate(a_ids, b_ids, store):
            tg = imp.target(df, role, b_ids)
            S = scores(df[df.match_id.isin(a_ids)], role, lam)
            for name, (ak, w) in CANDS.items():
                comp, el = S[ak]
                s = composite(comp, el, weights=w).set_index("player_id").rating
                common = s.index.intersection(tg.index)
                if len(common) < 15:
                    store[name].append((np.nan, np.nan)); continue
                ww = tg.loc[common, "unit"].values
                store[name].append((imp.wspearman(s[common].values, tg.loc[common, "nrae100"].values, ww),
                                    imp.wspearman(s[common].values, tg.loc[common, "wpa100"].values, ww)))
        for sp in random_splits(mids, n_splits):
            evaluate(mids[sp], mids[~sp], trials)
            evaluate(mids[~sp], mids[sp], trials)
        base = np.array(trials["spec composite (phase 1-2)"])
        for name in CANDS:
            v = np.array(trials[name]); d = v - base
            rows.append(dict(role=role, candidate=name, pred_nrae=np.nanmean(v[:, 0]), pred_wpa=np.nanmean(v[:, 1]),
                             d_nrae_vs_spec=np.nanmean(d[:, 0]), d_nrae_se=np.nanstd(d[:, 0]) / np.sqrt(len(d)),
                             d_wpa_vs_spec=np.nanmean(d[:, 1]), d_wpa_se=np.nanstd(d[:, 1]) / np.sqrt(len(d))))
        # temporal holdout, never used for selection
        early, late = mids[year <= 2024], mids[year >= 2025]
        store = {k: [] for k in CANDS}
        evaluate(early, late, store)
        for name in CANDS:
            trows.append(dict(role=role, candidate=name, pred_nrae_2025_26=store[name][0][0], pred_wpa_2025_26=store[name][0][1]))
        print(f"  {role} done")
    save_table(pd.DataFrame(rows), "phase3_final_candidates.csv")
    save_table(pd.DataFrame(trows), "phase3_temporal.csv")
    pd.set_option("display.width", 220)
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print(pd.DataFrame(trows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
