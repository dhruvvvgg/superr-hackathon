"""V3 stage C: exploratory predictive-challenger ratings.

Batters: richer-baseline credit (bat_credit_v3), V2 settings plus a shrunk pace-versus-spin adjustment.
Bowlers: main credit, V2 settings with the wicket part of NRAE shrunk ten times harder than the runs part.
Candidate adoption is based on tuning trials only (paired z > 2). Legacy confirmation results are descriptive
only because earlier V3 iterations used them for gating; they are not an untouched holdout.
Rating = shrunk, opponent-adjusted, leverage-weighted NRAE per 100 balls. This challenger uses a 40-ball minimum; primary shortlist eligibility is defined separately by config.json.
Output: outputs/v3/ratings_*.csv, top10_*.csv, chosen_config.json (not the primary task shortlist).
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
from v3_lib import fit3
from v2_lib import rating_eligible_ids

OUT = os.path.join(ROOT, "outputs", "v3")
ANCHOR = pd.Timestamp("2026-11-01")
N_BOOT = 1000
MIN_PRESS, MIN_TOTAL = 40, 150
V2 = json.load(open(os.path.join(ROOT, "outputs", "v2", "chosen_config.json")))
CHOSEN = {
    "bat": dict({k: v for k, v in V2["bat"]["cfg"].items() if k != "role_prior"}, inter="pace", lam_inter=3000.0,
                credit="bat_credit_v3", evidence="structure.csv: inter pace lam 3000; score_xfeat vs score (richer baseline)"),
    "bowl": dict({k: v for k, v in V2["bowl"]["cfg"].items() if k != "role_prior"}, lam_wkt=V2["bowl"]["cfg"]["lam"] * 10,
                 credit="bowl_credit", evidence="structure.csv: lam_wkt x10"),
}
_G = {}


def _boot(i):
    df, role, cfg, mids = _G["df"], _G["role"], _G["cfg"], _G["mids"]
    rng = np.random.RandomState(SEED + 7000 + i)
    mult = np.bincount(rng.randint(0, len(mids), len(mids)), minlength=len(mids))
    return fit3(df, role, ANCHOR, mult=mult, **cfg).set_index("player_id").s_nrae.reindex(_G["ids"]).values


def main():
    print("V3 stage C: final ratings")
    json.dump(CHOSEN, open(os.path.join(OUT, "chosen_config.json"), "w"), indent=1)
    names = player_names()
    _, _, ipl26, nat = latest_teams(None, raw("competition_team_player_mapping"), None)
    for role, label in [("bat", "batters"), ("bowl", "bowlers")]:
        cfg = {k: v for k, v in CHOSEN[role].items() if k not in ("credit", "evidence")}
        df = pd.read_parquet(os.path.join(PROCESSED, f"{CHOSEN[role]['credit']}.parquet"))
        res = fit3(df, role, ANCHOR, **cfg).set_index("player_id")
        unit = df.faced if role == "bat" else pd.Series(1, index=df.index)
        press = df.pA.astype(bool)
        n_press = unit[press].groupby(df.player_id[press]).sum()
        n_total = unit.groupby(df.player_id).sum()
        recent = (df.year.isin([2025, 2026]) & (unit > 0)).groupby(df.player_id).any()
        ids = np.sort(np.asarray(res.index.intersection(
            rating_eligible_ids(df, role, ANCHOR, min_press=MIN_PRESS, min_total=MIN_TOTAL)
        )))
        print(f"  {label}: {len(res)} players, {len(ids)} eligible")
        _G.update(df=df, role=role, cfg=cfg, mids=np.sort(df.match_id.unique()), ids=ids)
        with mp.get_context("fork").Pool(4) as pool:
            B = np.array(pool.map(_boot, range(N_BOOT), chunksize=25))
        rk = (-B).argsort(axis=1).argsort(axis=1) + 1
        t = pd.DataFrame({"player_id": ids, "rating": res.loc[ids, "s_nrae"].values,
                          "runs_part": res.loc[ids, "s_runs"].values, "wicket_part": res.loc[ids, "s_wkt"].values})
        t["rank"] = t.rating.rank(ascending=False, method="first").astype(int)
        t["boot_rating_p10"] = np.nanpercentile(B, 10, axis=0)
        t["boot_rating_p90"] = np.nanpercentile(B, 90, axis=0)
        t["boot_rank_mean"] = rk.mean(0)
        t["boot_rank_p10"] = np.percentile(rk, 10, axis=0)
        t["boot_rank_p90"] = np.percentile(rk, 90, axis=0)
        t["boot_top10_prob"] = (rk <= 10).mean(0)
        t["n_press_balls"] = n_press.reindex(ids).values.astype(int)
        t["n_total_balls"] = n_total.reindex(ids).values.astype(int)
        t = t.merge(describe(df[df.player_id.isin(ids)], role, "pA"), on="player_id", how="left", validate="1:1")
        # Descriptive within-player pressure-vs-normal contrast. This is deliberately not part of rating.
        if role == "bat":
            t["raw_pressure_uplift"] = t.press_sr - t.normal_sr
            t["raw_pressure_uplift_unit"] = "strike-rate points (pressure minus normal)"
        else:
            t["raw_pressure_uplift"] = t.normal_econ - t.press_econ
            t["raw_pressure_uplift_unit"] = "runs per over saved (normal minus pressure economy)"
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
        print(top[["final_rank", "player_name", "rating", "runs_part", "wicket_part", "boot_rank_p10", "boot_rank_p90", "boot_top10_prob", "n_press_balls"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
