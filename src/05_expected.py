"""Stage 05: identity-free expected-value baselines (out-of-fold) and the wicket value table.

Batter unit: every delivery faced (not a wide). Bowler unit: a legal-ball slot, i.e. one legal
ball plus the wides and no-balls that preceded it.

Outputs
  data/interim/bat_rows.parquet, data/interim/bowl_rows.parquet (with x_runs, x_wkt, wicket value)
  outputs/tables/resource_table.csv, expected_model_metrics.csv
"""
import os

import lightgbm as lgb
import numpy as np
import pandas as pd

from common import CFG, INTERIM, SEED, save_table, checked_merge
from res_lib import fit_resource, resource, wicket_value
from wp_lib import TIER_CODE

PHASE_CODE = {"powerplay": 0, "middle": 1, "death": 2}
BASE_FEATS = ["innings", "phase_c", "balls_left", "wkts_before", "crr", "rrr", "rrr_gap", "venue_avg",
              "tier_c", "is_pace", "bowl_type_c", "bat_lhb"]
ROLE_FEATS = ["bf_before", "batting_order"] if CFG.get("baseline", {}).get("role_aware") else []
BAT_FEATS = BASE_FEATS + ["is_noball_i", "free_hit_i"] + ROLE_FEATS
BOWL_FEATS = BASE_FEATS + ["free_hit_i"] + ROLE_FEATS

PARAMS = dict(learning_rate=0.05, n_estimators=300, num_leaves=31, min_child_samples=300,
              subsample=0.8, subsample_freq=1, colsample_bytree=0.9, reg_lambda=5.0,
              random_state=SEED, n_jobs=4, deterministic=True, force_row_wise=True, verbose=-1)


def oof(X, y, fold, objective, extra=None):
    pred = np.full(len(y), np.nan)
    for k in sorted(np.unique(fold)):
        tr, te = fold != k, fold == k
        p = dict(PARAMS, objective=objective, **(extra or {}))
        if objective == "binary":
            mdl = lgb.LGBMClassifier(**p).fit(X[tr], y[tr])
            pred[te] = mdl.predict_proba(X[te])[:, 1]
        else:
            mdl = lgb.LGBMRegressor(**p).fit(X[tr], y[tr])
            pred[te] = mdl.predict(X[te])
    return pred


def add_feats(d):
    d["phase_c"] = d.phase.map(PHASE_CODE)
    d["tier_c"] = d.tier.map(TIER_CODE)
    d["is_pace"] = (d.pace_or_spin == "Pace").astype(int)
    d["bowl_type_c"] = d.bowling_type.astype("category").cat.codes
    d["bat_lhb"] = (d.batting_type == "LHB").astype(int)
    d["is_noball_i"] = d.is_noball.astype(int)
    d["free_hit_i"] = d.free_hit.astype(int)
    d["rrr"] = d.rrr.clip(upper=40)
    d["rrr_gap"] = d.rrr_gap.clip(-40, 40)
    return d


def main():
    print("Stage 05: expected-value baselines")
    b = pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))
    b = b[b.clean].reset_index(drop=True)
    pr = pd.read_parquet(os.path.join(INTERIM, "pressure.parquet"))
    b = checked_merge(b, pr, "deliveries+pressure", on=["match_id", "innings", "innings_ball_num"],
                      how="left", validate="1:1")
    b = add_feats(b)
    # balls already faced by the striker in this innings (wides are not faced)
    nw = (~b.is_wide).astype(int)
    b["bf_before"] = nw.groupby([b.match_id, b.innings, b.striker_id]).cumsum() - nw
    bowler_w = set(CFG["bowler_wickets"])
    no_cost = set(CFG["non_batter_cost_dismissals"])
    b["wkt_cost"] = b.is_wicket & ~b.dismissal_type.isin(no_cost)          # counts against a batter
    b["striker_out"] = b.wkt_cost & (b.dismissed_player_id == b.striker_id)
    b["bowler_wkt"] = b.is_wicket & b.dismissal_type.isin(bowler_w)
    n_missing = int((b.wkt_cost & b.dismissed_player_id.isna()).sum())
    print(f"  wicket rows with missing dismissed_player_id (charged to nobody): {n_missing}")

    # ---- resource table and wicket value (first innings of clean matches) -----------------------
    i1 = b.innings == 1
    rp = fit_resource(b.balls_left[i1], b.wkts_before[i1], b.rem_runs[i1])
    grid = [(bl, w, resource(rp, bl, w), float(wicket_value(rp, bl, w)))
            for w in range(10) for bl in (120, 90, 60, 36, 24, 12, 6, 1)]
    emp = b[i1].groupby(["wkts_before", "balls_left"]).rem_runs.agg(["mean", "count"])
    rt = pd.DataFrame(grid, columns=["balls_left", "wickets_lost", "expected_remaining_runs", "wicket_value_runs"])
    rt["empirical_mean"] = [emp["mean"].get((w, bl), np.nan) for bl, w in zip(rt.balls_left, rt.wickets_lost)]
    rt["empirical_n"] = [emp["count"].get((w, bl), 0) for bl, w in zip(rt.balls_left, rt.wickets_lost)]
    save_table(rt, "resource_table.csv")
    b["wkt_value"] = wicket_value(rp, b.balls_left.values, b.wkts_before.values)
    print(f"  wicket value (runs): mean {b.wkt_value.mean():.2f}, powerplay {b[b.phase == 'powerplay'].wkt_value.mean():.2f}, "
          f"death {b[b.phase == 'death'].wkt_value.mean():.2f}")

    # ---- batter rows ---------------------------------------------------------------------------------
    bat = b[~b.is_wide].copy()
    print(f"  batter rows: {len(b)} deliveries -> {len(bat)} faced (wides removed: {int(b.is_wide.sum())})")
    Xb = bat[BAT_FEATS].values.astype(float)
    bat["x_runs"] = oof(Xb, bat.runs.values.astype(float), bat.fold.values, "regression")
    bat["x_wkt"] = oof(Xb, bat.striker_out.values.astype(int), bat.fold.values, "binary")

    # ---- bowler slots ----------------------------------------------------------------------------------
    b["slot"] = b.legal_before
    last_legal = b.groupby(["match_id", "innings"]).legal_before.transform("max")
    tail_no_legal = (~b.legal) & (b.legal_before == last_legal) & \
        (~b.groupby(["match_id", "innings", "legal_before"]).legal.transform("any"))
    b.loc[tail_no_legal, "slot"] = b.loc[tail_no_legal, "slot"] - 1
    print(f"  trailing illegal deliveries merged into the previous slot: {int(tail_no_legal.sum())}")
    gs = b.groupby(["match_id", "innings", "slot"], sort=False)
    agg = gs.agg(bowler_runs=("bowler_runs", "sum"), bowler_wkt=("bowler_wkt", "sum"),
                 wpa=("wpa", "sum"), n_deliveries=("runs", "size")).reset_index()
    first = gs.head(1).drop(columns=["bowler_runs", "bowler_wkt", "wpa"])
    # the bowler of a slot is the bowler of its legal ball
    legal_rows = b[b.legal][["match_id", "innings", "slot", "bowler_id", "bowler_name", "bowling_type",
                             "pace_or_spin"]].drop_duplicates(["match_id", "innings", "slot"])
    first = first.drop(columns=["bowler_id", "bowler_name", "bowling_type", "pace_or_spin"])
    bowl = checked_merge(first, agg, "slot first row+slot totals", on=["match_id", "innings", "slot"], how="left", validate="1:1")
    bowl = checked_merge(bowl, legal_rows, "slots+bowler of legal ball", on=["match_id", "innings", "slot"],
                         how="inner", validate="1:1", allow_drop=True)
    bowl = add_feats(bowl)
    assert len(bowl) == int(b.legal.sum()), (len(bowl), int(b.legal.sum()))
    print(f"  bowler slots: {len(bowl)} (= legal balls {int(b.legal.sum())})")
    Xw = bowl[BOWL_FEATS].values.astype(float)
    bowl["x_runs"] = oof(Xw, bowl.bowler_runs.values.astype(float), bowl.fold.values, "regression")
    bowl["x_wkt"] = oof(Xw, (bowl.bowler_wkt.values > 0).astype(int), bowl.fold.values, "binary")

    # ---- metrics ---------------------------------------------------------------------------------------
    def rmse(a, p):
        return float(np.sqrt(np.mean((a - p) ** 2)))

    def ll(a, p):
        p = np.clip(p, 1e-6, 1 - 1e-6)
        return float(-np.mean(a * np.log(p) + (1 - a) * np.log(1 - p)))

    rows = []
    for name, d, yr, yw in [("batter", bat, "runs", "striker_out"), ("bowler", bowl, "bowler_runs", "bowler_wkt")]:
        ph_mean_r = d.groupby(["innings", "phase"])[yr].transform("mean")
        ph_mean_w = d.groupby(["innings", "phase"])[yw].transform("mean")
        rows += [dict(model=f"{name} xRuns", n=len(d), metric="RMSE", oof=rmse(d[yr], d.x_runs),
                      phase_mean_baseline=rmse(d[yr], ph_mean_r), mean_actual=d[yr].mean(), mean_pred=d.x_runs.mean()),
                 dict(model=f"{name} xWkt", n=len(d), metric="log loss", oof=ll(d[yw].astype(float), d.x_wkt),
                      phase_mean_baseline=ll(d[yw].astype(float), ph_mean_w), mean_actual=d[yw].mean(), mean_pred=d.x_wkt.mean())]
        for t in ["Low", "Normal", "High", "Extreme"]:
            s = d[d.ptier == t]
            rows.append(dict(model=f"{name} residual by tier: {t}", n=len(s), metric="mean (actual - expected) runs per ball",
                             oof=(s[yr] - s.x_runs).mean(), phase_mean_baseline=np.nan,
                             mean_actual=s[yr].mean(), mean_pred=s.x_runs.mean()))
    save_table(pd.DataFrame(rows), "expected_model_metrics.csv")
    print(pd.DataFrame(rows).round(4).to_string())

    bat.to_parquet(os.path.join(INTERIM, "bat_rows.parquet"), index=False)
    bowl.to_parquet(os.path.join(INTERIM, "bowl_rows.parquet"), index=False)
    b[["match_id", "innings", "innings_ball_num", "wkt_value", "wkt_cost", "striker_out", "bowler_wkt", "slot"]] \
        .to_parquet(os.path.join(INTERIM, "ball_extras.parquet"), index=False)
    np.save(os.path.join(INTERIM, "resource_params.npy"), rp)


if __name__ == "__main__":
    main()
