"""Model-quality scorecard for one pipeline variant (phase 2). Reads the files of the current
SUPERR_TAG and writes quality.json. Nothing here looks at who is in the top 10."""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json

import numpy as np
import pandas as pd

from common import CFG, INTERIM, PROCESSED, TABLES, TAG
from ratings_lib import Prep, rate, composite
from robust_lib import bootstrap, split_half, random_splits


def main(n_boot=200):
    q = dict(tag=TAG or "main")
    wm = pd.read_csv(os.path.join(TABLES, "wp_model_metrics.csv"))
    for s, k in [("all", "wp_logloss"), ("innings 1", "wp_logloss_inn1"), ("innings 2", "wp_logloss_inn2")]:
        q[k] = wm[(wm.role == "primary") & (wm["sample"] == s)].log_loss.iloc[0]
    q["wp_max_calib_gap"] = wm[(wm.role == "primary") & (wm["sample"] == "all")].max_calib_gap_dense_bins.iloc[0]
    lv = pd.read_csv(os.path.join(TABLES, "leverage_validity.csv")).iloc[0]
    q["lev_spearman_abs_wpa"] = lv.spearman_leverage_vs_realised_abs_wpa
    q["lev_pearson_abs_wpa"] = lv.pearson_leverage_vs_realised_abs_wpa
    em = pd.read_csv(os.path.join(TABLES, "expected_model_metrics.csv")).set_index("model").oof
    q.update(bat_xruns_rmse=em["batter xRuns"], bat_xwkt_logloss=em["batter xWkt"],
             bowl_xruns_rmse=em["bowler xRuns"], bowl_xwkt_logloss=em["bowler xWkt"])
    cv = pd.read_csv(os.path.join(TABLES, "ridge_cv.csv"))
    lam = json.load(open(os.path.join(INTERIM, "lambdas.json")))
    for role, fname in [("bat", "bat_credit"), ("bowl", "bowl_credit")]:
        df = pd.read_parquet(os.path.join(PROCESSED, f"{fname}.parquet"))
        l = (lam[role]["lambda_main"], lam[role]["lambda_delta"])
        q[f"{role}_ridge_cv_wmse"] = cv[(cv.role == role) & cv.chosen].cv_wmse.iloc[0]
        q[f"{role}_nrae_var"] = float(df.nrae.var())
        mids = np.sort(df.match_id.unique())
        res = split_half(df, role, l, random_splits(mids, CFG["robustness"]["n_random_splits"]))
        q[f"{role}_splithalf_rating"] = res.rating.mean()
        q[f"{role}_splithalf_rating_se"] = res.rating.std() / np.sqrt(len(res))
        for c in ("level", "impact", "consistency", "delta"):
            q[f"{role}_splithalf_{c}"] = res[c].mean()
        yr = df.drop_duplicates("match_id").set_index("match_id").year.reindex(mids).values
        q[f"{role}_season_persistence"] = split_half(df, role, l, [yr <= 2024]).rating.iloc[0]
        prep = Prep(df, role)
        elig = prep.eligible()
        t = composite(rate(prep, *l), elig).sort_values("player_id")
        ids, (rk, rating, _, _) = bootstrap(prep, l, elig, n_boot)
        point = t["rank"].values
        top10, top20 = point <= 10, point <= 20
        q[f"{role}_boot_top10_prob_of_top10"] = float((rk[:, top10] <= 10).mean())
        q[f"{role}_boot_rank_iqr80_top20"] = float((np.percentile(rk[:, top20], 90, axis=0) - np.percentile(rk[:, top20], 10, axis=0)).mean())
        q[f"{role}_n_eligible"] = int(elig.sum())
    json.dump(q, open(os.path.join(TABLES, "quality.json"), "w"), indent=1)
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in q.items()}))


if __name__ == "__main__":
    main()
