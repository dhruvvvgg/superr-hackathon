"""V2 stage B: final ratings from the configuration chosen in stage A.

Rating = the forward-window-selected score variant: shrunk, opponent-adjusted leverage-weighted NRAE,
WPA, or the selected standardised NRAE/WPA blend. Blend scores are unitless. Ranking uses the common
eligible-player universe, with a match-cluster bootstrap for rank and rating intervals.

Eligibility: at least 40 pressure balls (the same bar used in the validation trials), at least 150 balls in
total, and at least one appearance in 2025 or 2026.
Output: outputs/v2/ratings_batters.csv, ratings_bowlers.csv, top10_batters.csv, top10_bowlers.csv
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json
import multiprocessing as mp

import numpy as np
import pandas as pd

from common import PROCESSED, ROOT, SEED, raw, player_names
from ratings_lib import describe, latest_teams
from v2_lib import fit, rating_eligible_ids

OUT = os.path.join(ROOT, "outputs", "v2")
ANCHOR = pd.Timestamp("2026-11-01")
N_BOOT = 1000
MIN_PRESS, MIN_TOTAL = 40, 150
_G = {}


def score_values(res, score):
    """Apply the exact score variant selected by stage 20 to a fixed player universe."""
    q = res
    if score == "nrae":
        return q.s_nrae.to_numpy(dtype=float)
    if score == "wpa":
        return q.s_wpa.to_numpy(dtype=float)
    if score.startswith("blend"):
        beta = float(score.replace("blend", ""))
        sd_n = float(q.s_nrae.std())
        sd_w = float(q.s_wpa.std())
        if sd_n <= 0 or sd_w <= 0:
            raise ValueError("Cannot blend V2 scores with zero cross-player variance")
        return ((q.s_nrae - q.s_nrae.mean()) / sd_n +
                beta * (q.s_wpa - q.s_wpa.mean()) / sd_w).to_numpy(dtype=float)
    raise ValueError(f"Unsupported V2 score variant: {score}")


def _boot(i):
    df, role, cfg, mids = _G["df"], _G["role"], _G["cfg"], _G["mids"]
    rng = np.random.RandomState(SEED + 5000 + i)
    mult = np.bincount(rng.randint(0, len(mids), len(mids)), minlength=len(mids))
    r = fit(df, role, ANCHOR, mult=mult, **cfg).set_index("player_id")
    return score_values(r.loc[_G["ids"]], _G["score"])


def main():
    print("V2 stage B: final ratings")
    chosen = json.load(open(os.path.join(OUT, "chosen_config.json")))
    names = player_names()
    mapping = raw("competition_team_player_mapping")
    ipl_team, ipl_season, ipl26, nat = latest_teams(None, mapping, None)
    for role, fname, label in [("bat", "bat_credit", "batters"), ("bowl", "bowl_credit", "bowlers")]:
        df = pd.read_parquet(os.path.join(PROCESSED, f"{fname}.parquet"))
        cfg = chosen[role]["cfg"]
        score = chosen[role]["score"]
        res = fit(df, role, ANCHOR, **cfg).set_index("player_id")
        unit = df.faced if role == "bat" else pd.Series(1, index=df.index)
        press = df.pA.astype(bool)
        n_press = unit[press].groupby(df.player_id[press]).sum()
        n_total = unit.groupby(df.player_id).sum()
        recent = (df.year.isin([2025, 2026]) & (unit > 0)).groupby(df.player_id).any()
        elig = res.index.intersection(
            rating_eligible_ids(df, role, ANCHOR, min_press=MIN_PRESS, min_total=MIN_TOTAL)
        )
        print(f"  {label}: {len(res)} players, {len(elig)} eligible")
        ids = np.sort(np.array(elig))
        _G.update(df=df, role=role, cfg=cfg, score=score, mids=np.sort(df.match_id.unique()), ids=ids)
        with mp.get_context("fork").Pool(4) as pool:
            B = np.array(pool.map(_boot, range(N_BOOT), chunksize=25))
        rk = (-B).argsort(axis=1).argsort(axis=1) + 1
        t = pd.DataFrame({"player_id": ids})
        t["rating"] = score_values(res.loc[ids], score)
        t["rating_score"] = score
        t["nrae_per100_shrunk"] = res.loc[ids, "s_nrae"].values
        t["rank"] = t.rating.rank(ascending=False, method="first").astype(int)
        t["boot_rating_p10"] = np.nanpercentile(B, 10, axis=0)
        t["boot_rating_p90"] = np.nanpercentile(B, 90, axis=0)
        t["boot_rank_mean"] = rk.mean(0)
        t["boot_rank_p10"] = np.percentile(rk, 10, axis=0)
        t["boot_rank_p90"] = np.percentile(rk, 90, axis=0)
        t["boot_top10_prob"] = (rk <= 10).mean(0)
        t["wpa_per100_shrunk"] = res.loc[ids, "s_wpa"].values
        t["n_press_balls"] = n_press.reindex(ids).values.astype(int)
        t["n_total_balls"] = n_total.reindex(ids).values.astype(int)
        desc = describe(df[df.player_id.isin(ids)], role, "pA")
        t = t.merge(desc, on="player_id", how="left", validate="1:1")
        t.insert(1, "player_name", t.player_id.map(names))
        t["ipl_2026_team"] = t.player_id.map(ipl26)
        t["national_team"] = t.player_id.map(nat)
        t = t.sort_values("rank")
        assert t.player_id.is_unique and t.player_name.notna().all()
        t.to_csv(os.path.join(OUT, f"ratings_{label}.csv"), index=False, float_format="%.6g")
        top = t.head(10).copy()
        top.insert(0, "final_rank", range(1, 11))
        top.insert(3, "dropdown_name", top.player_name)
        top.to_csv(os.path.join(OUT, f"top10_{label}.csv"), index=False, float_format="%.6g")
        print(top[["final_rank", "player_name", "rating", "boot_rating_p10", "boot_rating_p90", "boot_rank_p10", "boot_rank_p90", "boot_top10_prob", "n_press_balls"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
