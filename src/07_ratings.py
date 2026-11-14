"""Stage 07: player ratings under the primary specification.

Outputs
  outputs/tables/batter_ratings.csv, bowler_ratings.csv   every eligible player with components
  outputs/tables/ridge_cv.csv, estimator_agreement.csv
  data/interim/lambdas.json
"""
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import CFG, INTERIM, PROCESSED, TABLES, raw, player_names, save_table, checked_merge
from ratings_lib import Prep, rate, composite, describe, latest_teams, COMPONENTS


def main():
    print("Stage 07: ratings")
    names = player_names()
    mapping = raw("competition_team_player_mapping")
    ipl_team, ipl_season, ipl26, nat = latest_teams(None, mapping, None)
    lam, cv_tabs, agree = {}, [], []
    for role, fname, out in [("bat", "bat_credit", "batter_ratings.csv"), ("bowl", "bowl_credit", "bowler_ratings.csv")]:
        d = pd.read_parquet(os.path.join(PROCESSED, f"{fname}.parquet"))
        prep = Prep(d, role, pcol="p" + CFG["pressure"]["primary_variant"])
        lm, ld, tab = prep.cv_lambdas()
        lam[role] = dict(lambda_main=lm, lambda_delta=ld)
        cv_tabs.append(tab.assign(role=role, chosen=(tab.lambda_main == lm) & (tab.lambda_delta == ld)))
        edge = (ld == max(CFG["ridge"]["lambda_delta_grid"])) or (lm in (min(CFG["ridge"]["lambda_main_grid"]), max(CFG["ridge"]["lambda_main_grid"])))
        print(f"  {role}: lambda_main={lm:g}, lambda_delta={ld:g}{' (edge of grid)' if edge else ''}")

        comp = rate(prep, lm, ld)
        elig = prep.eligible()
        n_eligible = int(elig.sum())
        min_pool = int(CFG["eligibility"]["min_pool"])
        if n_eligible < min_pool:
            raise RuntimeError(
                f"{role}: only {n_eligible} players meet the registered eligibility thresholds; "
                f"required minimum pool is {min_pool}. Thresholds will not be relaxed to fill the pool."
            )
        print(f"  {role}: {prep.P} players -> {n_eligible} eligible (registered thresholds, no relaxation)")
        t = composite(comp, elig)
        t_eb = composite(comp, elig, estimator="eb").set_index("player_id")
        t["rating_eb"] = t.player_id.map(t_eb.rating)
        t["rank_eb"] = t.player_id.map(t_eb["rank"])
        agree.append(dict(role=role, quantity="level: ridge vs empirical Bayes", n=len(t),
                          spearman=spearmanr(t.level, t.level_eb).statistic))
        agree.append(dict(role=role, quantity="delta: ridge vs empirical Bayes", n=len(t),
                          spearman=spearmanr(t.delta, t.delta_eb).statistic))
        agree.append(dict(role=role, quantity="composite rating: ridge vs empirical Bayes", n=len(t),
                          spearman=spearmanr(t.rating, t.rating_eb).statistic))
        agree.append(dict(role=role, quantity="top-10 overlap: ridge vs empirical Bayes", n=10,
                          spearman=len(set(t[t["rank"] <= 10].player_id) & set(t[t.rank_eb <= 10].player_id)) / 10))
        for a in COMPONENTS:
            for b_ in COMPONENTS:
                if a < b_:
                    agree.append(dict(role=role, quantity=f"component correlation: {a} vs {b_}", n=len(t),
                                      spearman=spearmanr(t[a], t[b_]).statistic))

        desc = describe(d[d.player_id.isin(t.player_id)], role, prep.pcol)
        t = checked_merge(t, desc, f"{role} ratings+descriptives", on="player_id", how="left", validate="1:1")
        t.insert(1, "player_name", t.player_id.map(names))
        assert t.player_name.notna().all() and t.player_id.is_unique
        t["ipl_2026_team"] = t.player_id.map(ipl26)
        t["latest_ipl_team"] = t.player_id.map(ipl_team)
        t["latest_ipl_season"] = t.player_id.map(ipl_season)
        t["national_team"] = t.player_id.map(nat)
        t["n_press_balls"] = t.player_id.map(dict(zip(prep.players, prep.n_press)))
        t["n_press_innings"] = t.player_id.map(dict(zip(prep.players, prep.n_press_inn)))
        t["n_total_balls"] = t.player_id.map(dict(zip(prep.players, prep.n_total)))
        t["dips_under_pressure"] = t.z_delta <= -1.0
        front = ["rank", "player_id", "player_name", "rating", "z_level", "z_impact", "z_consistency", "z_delta",
                 "level", "normal", "delta", "impact", "consistency", "hit_rate", "downside",
                 "n_press_balls", "n_press_innings", "n_total_balls"]
        t = t[front + [c for c in t.columns if c not in front]].sort_values("rank")
        save_table(t, out)
    json.dump(lam, open(os.path.join(INTERIM, "lambdas.json"), "w"))
    save_table(pd.concat(cv_tabs), "ridge_cv.csv")
    save_table(pd.DataFrame(agree), "estimator_agreement.csv")
    print(pd.DataFrame(agree).round(3).to_string())


if __name__ == "__main__":
    main()
