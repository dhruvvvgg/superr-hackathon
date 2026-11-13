"""Stage 05: identity-free expected-value baselines and wicket values with chronological cross-fitting.

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

from common import CFG, INTERIM, SEED, save_table, checked_merge, train_mask_for_fold
from res_lib import fit_resource, resource, wicket_value
from wp_lib import TIER_CODE

PHASE_CODE = {"powerplay": 0, "middle": 1, "death": 2}
BASE_FEATS = ["innings", "phase_c", "balls_left", "wkts_before", "crr", "rrr", "rrr_gap", "venue_avg",
              "tier_c", "is_pace", "bowl_type_c", "bat_lhb"]
ROLE_FEATS = ["bf_before", "batting_order"] if CFG.get("baseline", {}).get("role_aware") else []
# situational extras (identity-free): momentum, live win probability, ball in over, partnership, bowler workload
_XF = ["runs_last12", "wkts_last12", "dot_streak", "wp_before", "ball_in_over", "partnership_balls", "bowler_balls_before"]
_XS = CFG.get("baseline", {}).get("extra_feats")          # False, True / "both", "bat" or "bowl"
BAT_FEATS = BASE_FEATS + ["is_noball_i", "free_hit_i"] + ROLE_FEATS + (_XF if _XS in (True, "both", "bat") else [])
BOWL_FEATS = BASE_FEATS + ["free_hit_i"] + ROLE_FEATS + (_XF if _XS in (True, "both", "bowl") else [])

PARAMS = dict(learning_rate=0.05, n_estimators=300, num_leaves=31, min_child_samples=300,
              subsample=0.8, subsample_freq=1, colsample_bytree=0.9, reg_lambda=5.0,
              random_state=SEED, n_jobs=4, deterministic=True, force_row_wise=True, verbose=-1)


def phase_mean_oof(y, fold, innings, phase):
    """Past-fold-only innings/phase mean baseline; never estimates from the scored fold."""
    y = np.asarray(y, dtype=float)
    fold = np.asarray(fold)
    innings = np.asarray(innings)
    phase = np.asarray(phase)
    pred = np.full(len(y), np.nan)
    for k in sorted(np.unique(fold)):
        tr, te = train_mask_for_fold(fold, k), fold == k
        if not tr.any() or not te.any():
            raise ValueError(f"Empty phase-mean train/test split for fold {k}")
        stats = (pd.DataFrame({"innings": innings[tr], "phase": phase[tr], "y": y[tr]})
                 .groupby(["innings", "phase"]).y.mean())
        keys = pd.MultiIndex.from_arrays([innings[te], phase[te]])
        vals = stats.reindex(keys).to_numpy(dtype=float, copy=True)
        vals[~np.isfinite(vals)] = float(np.mean(y[tr]))
        pred[te] = vals
    if not np.isfinite(pred).all():
        raise AssertionError("Phase-mean OOF baseline contains missing predictions")
    return pred


def oof(X, y, fold, objective, extra=None, match_ids=None, match_dates=None):
    """Out-of-fold predictions; regression gets fold-local bias correction.

    Calibration/bias estimation uses only a match-held-out subset of the training fold.
    Forward folds use the latest 20% of training matches; warm-up peer folds use a
    deterministic grouped split. The final estimator is refit on the full training fold.
    """
    pred = np.full(len(y), np.nan)
    match_ids = np.asarray(match_ids) if match_ids is not None else None
    dates = pd.to_datetime(match_dates).to_numpy() if match_dates is not None else None
    for k in sorted(np.unique(fold)):
        tr, te = train_mask_for_fold(fold, k), fold == k
        if not tr.any() or not te.any():
            raise ValueError(f"Empty expected-value train/test split for fold {k}")
        p = dict(PARAMS, objective=objective, **(extra or {}))
        bias = 0.0
        if match_ids is not None and match_dates is not None:
            train_matches = np.unique(match_ids[tr])
            if len(train_matches) >= 10:
                if k >= 0:
                    match_date = pd.DataFrame({"match_id": match_ids[tr], "date": dates[tr]}).drop_duplicates("match_id")
                    ordered = match_date.sort_values(["date", "match_id"]).match_id.to_numpy()
                    cal_matches = ordered[-max(1, int(np.ceil(0.20 * len(ordered)))):]
                else:
                    rng = np.random.RandomState(SEED + abs(int(k)))
                    shuffled = rng.permutation(train_matches)
                    cal_matches = shuffled[:max(1, int(np.ceil(0.20 * len(shuffled))))]
                cal = tr & np.isin(match_ids, cal_matches)
                fit = tr & ~cal
                if fit.any() and cal.any():
                    if objective == "regression":
                        pilot = lgb.LGBMRegressor(**p).fit(X[fit], y[fit])
                        bias = float(np.mean(y[cal] - pilot.predict(X[cal])))
                    elif objective == "binary":
                        # Keep the candidate classifier available for diagnostics, but calibrate
                        # its probabilities using only held-out training matches.
                        from sklearn.linear_model import LogisticRegression
                        pilot = lgb.LGBMClassifier(**p).fit(X[fit], y[fit])
                        cp = np.clip(pilot.predict_proba(X[cal])[:, 1], 1e-5, 1 - 1e-5)
                        clogit = np.log(cp / (1 - cp)).reshape(-1, 1)
                        if np.unique(y[cal]).size == 2:
                            calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
                            calibrator.fit(clogit, y[cal])
                        else:
                            calibrator = None
                    else:
                        calibrator = None
                else:
                    calibrator = None
            else:
                calibrator = None
        else:
            calibrator = None
        if objective == "binary":
            mdl = lgb.LGBMClassifier(**p).fit(X[tr], y[tr])
            raw = np.clip(mdl.predict_proba(X[te])[:, 1], 1e-5, 1 - 1e-5)
            if calibrator is not None:
                raw_logit = np.log(raw / (1 - raw)).reshape(-1, 1)
                pred[te] = calibrator.predict_proba(raw_logit)[:, 1]
            else:
                pred[te] = raw
        else:
            mdl = lgb.LGBMRegressor(**p).fit(X[tr], y[tr])
            pred[te] = mdl.predict(X[te]) + bias
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
    b["ball_in_over"] = b.legal_before % 6
    wk_no = b.groupby(["match_id", "innings"]).is_wicket.cumsum() - b.is_wicket
    lg = b.legal.astype(int)
    b["partnership_balls"] = lg.groupby([b.match_id, b.innings, wk_no]).cumsum() - lg
    b["bowler_balls_before"] = lg.groupby([b.match_id, b.innings, b.bowler_id]).cumsum() - lg
    bowler_w = set(CFG["bowler_wickets"])
    no_cost = set(CFG["non_batter_cost_dismissals"])
    b["wkt_cost"] = b.is_wicket & ~b.dismissal_type.isin(no_cost)          # counts against a batter
    b["striker_out"] = b.wkt_cost & (b.dismissed_player_id == b.striker_id)
    b["bowler_wkt"] = b.is_wicket & b.dismissal_type.isin(bowler_w)
    n_missing = int((b.wkt_cost & b.dismissed_player_id.isna()).sum())
    print(f"  wicket rows with missing dismissed_player_id (charged to nobody): {n_missing}")

    # ---- resource table and wicket value (first innings of clean matches) -----------------------
    i1 = b.innings == 1
    fold_values = sorted(b.fold.unique().tolist())
    fold_audit = []
    for k in fold_values:
        tr_fold = train_mask_for_fold(b.fold.values, k)
        te_fold = b.fold.values == k
        tr_dates = pd.to_datetime(b.loc[tr_fold, "match_date"])
        te_dates = pd.to_datetime(b.loc[te_fold, "match_date"])
        fold_audit.append(dict(fold=int(k), kind="warmup_crossfit" if k < 0 else "forward_temporal",
                               train_matches=int(b.loc[tr_fold, "match_id"].nunique()),
                               test_matches=int(b.loc[te_fold, "match_id"].nunique()),
                               train_max_date=tr_dates.max().date().isoformat(),
                               test_min_date=te_dates.min().date().isoformat(),
                               future_train_matches=int(b.loc[tr_fold & (pd.to_datetime(b.match_date).values >= te_dates.min()),
                                                               "match_id"].nunique())))
    save_table(pd.DataFrame(fold_audit), "expected_fold_audit.csv")
    wkt_value = np.full(len(b), np.nan)
    resource_models = {}
    for k in fold_values:
        tr = train_mask_for_fold(b.fold.values, k) & i1.values
        te = (b.fold.values == k)
        rp_k = fit_resource(b.balls_left.values[tr], b.wkts_before.values[tr], b.rem_runs.values[tr])
        resource_models[k] = rp_k
        wkt_value[te] = wicket_value(rp_k, b.balls_left.values[te], b.wkts_before.values[te])
    if np.isnan(wkt_value).any():
        raise AssertionError("Wicket values missing for one or more temporal folds")
    # The final fold resource table is the latest historical fit; per-row values remain fold-specific.
    rp = resource_models[max(fold_values)]
    grid = [(bl, w, resource(rp, bl, w), float(wicket_value(rp, bl, w)))
            for w in range(10) for bl in (120, 90, 60, 36, 24, 12, 6, 1)]
    latest_train = train_mask_for_fold(b.fold.values, max(fold_values))
    emp = b[i1 & latest_train].groupby(["wkts_before", "balls_left"]).rem_runs.agg(["mean", "count"])
    rt = pd.DataFrame(grid, columns=["balls_left", "wickets_lost", "expected_remaining_runs", "wicket_value_runs"])
    rt["empirical_mean"] = [emp["mean"].get((w, bl), np.nan) for bl, w in zip(rt.balls_left, rt.wickets_lost)]
    rt["empirical_n"] = [emp["count"].get((w, bl), 0) for bl, w in zip(rt.balls_left, rt.wickets_lost)]
    save_table(rt, "resource_table.csv")
    b["wkt_value"] = wkt_value
    print(f"  wicket value (runs): mean {b.wkt_value.mean():.2f}, powerplay {b[b.phase == 'powerplay'].wkt_value.mean():.2f}, "
          f"death {b[b.phase == 'death'].wkt_value.mean():.2f}")

    # ---- batter rows ---------------------------------------------------------------------------------
    bat = b[~b.is_wide].copy()
    print(f"  batter rows: {len(b)} deliveries -> {len(bat)} faced (wides removed: {int(b.is_wide.sum())})")
    Xb = bat[BAT_FEATS].values.astype(float)
    bat["x_runs"] = oof(Xb, bat.runs.values.astype(float), bat.fold.values, "regression", match_ids=bat.match_id.values, match_dates=bat.match_date.values)
    bat["x_wkt_model"] = oof(Xb, bat.striker_out.values.astype(int), bat.fold.values, "binary",
                            match_ids=bat.match_id.values, match_dates=bat.match_date.values)
    bat["x_wkt_baseline"] = phase_mean_oof(bat.striker_out.values.astype(int), bat.fold.values,
                                           bat.innings.values, bat.phase.values)
    # The simpler identity-free phase mean is the selected wicket baseline. The calibrated
    # classifier remains exported for diagnostics but is not allowed to worsen wicket credit.
    bat["x_wkt"] = bat["x_wkt_baseline"]

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
    bowl["x_runs"] = oof(Xw, bowl.bowler_runs.values.astype(float), bowl.fold.values, "regression", match_ids=bowl.match_id.values, match_dates=bowl.match_date.values)
    bowl["x_wkt_model"] = oof(Xw, (bowl.bowler_wkt.values > 0).astype(int), bowl.fold.values, "binary",
                             match_ids=bowl.match_id.values, match_dates=bowl.match_date.values)
    bowl["x_wkt_baseline"] = phase_mean_oof((bowl.bowler_wkt.values > 0).astype(int), bowl.fold.values,
                                             bowl.innings.values, bowl.phase.values)
    bowl["x_wkt"] = bowl["x_wkt_baseline"]

    # ---- metrics ---------------------------------------------------------------------------------------
    def rmse(a, p):
        return float(np.sqrt(np.mean((a - p) ** 2)))

    def ll(a, p):
        p = np.clip(p, 1e-6, 1 - 1e-6)
        return float(-np.mean(a * np.log(p) + (1 - a) * np.log(1 - p)))

    rows = []
    for name, d, yr, yw in [("batter", bat, "runs", "striker_out"), ("bowler", bowl, "bowler_runs", "bowler_wkt")]:
        yr_true = d[yr].to_numpy(dtype=float)
        yw_true = d[yw].to_numpy(dtype=float)
        run_base = phase_mean_oof(yr_true, d.fold.values, d.innings.values, d.phase.values)
        wkt_base = d.x_wkt_baseline.to_numpy(dtype=float)
        rows += [
            dict(model=f"{name} xRuns", n=len(d), metric="RMSE", oof=rmse(yr_true, d.x_runs),
                 phase_mean_baseline=rmse(yr_true, run_base), mean_actual=yr_true.mean(),
                 mean_pred=d.x_runs.mean(), selected_method="lightgbm"),
            dict(model=f"{name} xWkt candidate", n=len(d), metric="log loss",
                 oof=ll(yw_true, d.x_wkt_model), phase_mean_baseline=ll(yw_true, wkt_base),
                 mean_actual=yw_true.mean(), mean_pred=d.x_wkt_model.mean(), selected_method="diagnostic_only"),
            dict(model=f"{name} xWkt", n=len(d), metric="log loss",
                 oof=ll(yw_true, d.x_wkt), phase_mean_baseline=ll(yw_true, wkt_base),
                 mean_actual=yw_true.mean(), mean_pred=d.x_wkt.mean(), selected_method="fold_local_phase_mean")
        ]
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
