"""Stage 02: legal balls, extras calibration, score reconstruction, match state and features.

Outputs
  data/interim/balls.parquet        one row per delivery (innings 1-2, all matches with ball data)
  data/interim/match_info.parquet   one row per match with flags, totals and targets
  outputs/tables/extras_calibration.csv
  appends acceptance rows to outputs/tables/data_quality.csv
"""
import os

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from common import CFG, INTERIM, TABLES, raw, parse_result, checked_merge, save_table, phase_of_over

EXTRA_TYPES = ["wide", "Overstep", "other", "legbyes", "byes"]
PENALTY_RUNS = 5.0


def l1_fit(D, y, lo=1.0, hi=6.0):
    """Least absolute deviations fit of y ~ D v with lo <= v <= hi (linear programme)."""
    n, k = D.shape
    c = np.r_[np.zeros(k), np.ones(n)]
    A = np.block([[D, -np.eye(n)], [-D, -np.eye(n)]])
    bnd = [(lo, hi)] * k + [(0, None)] * n
    res = linprog(c, A_ub=A, b_ub=np.r_[y, -y], bounds=bnd, method="highs")
    assert res.success, res.message
    return res.x[:k]


def main():
    print("Stage 02: build state")
    b = raw("ball_by_ball")
    m = raw("matches")
    comp = raw("competitions")
    n_all = len(b)
    so = b[b.innings > 2]
    print(f"  super-over deliveries dropped: {len(so)} in {so.match_id.nunique()} matches")
    b = b[b.innings <= 2].sort_values(["match_id", "innings", "innings_ball_num"]).reset_index(drop=True)
    assert len(b) + len(so) == n_all
    assert not b.duplicated(["match_id", "innings", "innings_ball_num"]).any()

    # Preserve any source over identifier before deriving the legal-ball over index.
    source_over_col = next((c for c in ("over", "over_number", "over_num", "over_id") if c in b.columns), None)
    if source_over_col is not None:
        b["source_over"] = pd.to_numeric(b[source_over_col], errors="coerce")
        print(f"  preserved source over field: {source_over_col}")

    # Correct a verified ball-level identity error in the derived working copy only.
    ball_identity_audit = []
    for key, fix in CFG["source_overrides"].get("ball_identity_fixes", {}).items():
        mid, inn_no, ball_no = (int(x) for x in key.split(":"))
        sel = ((b.match_id == mid) & (b.innings == inn_no) & (b.innings_ball_num == ball_no))
        assert int(sel.sum()) == 1, f"ball identity override {key} did not match exactly one delivery"
        row = b.loc[sel].iloc[0]
        assert int(row.striker_id) == int(fix["raw_striker_id"]), f"override {key} striker no longer matches source"
        assert int(row.non_striker_id) == int(fix["raw_non_striker_id"]), f"override {key} non-striker no longer matches source"
        b.loc[sel, "non_striker_id"] = int(fix["corrected_non_striker_id"])
        ball_identity_audit.append(dict(match_id=mid, innings=inn_no, innings_ball_num=ball_no,
                                        striker_id=int(row.striker_id),
                                        raw_non_striker_id=int(row.non_striker_id),
                                        corrected_non_striker_id=int(fix["corrected_non_striker_id"]),
                                        evidence=fix["evidence"]))
        print(f"  verified ball identity override applied: match {mid}, innings {inn_no}, ball {ball_no}")
    save_table(pd.DataFrame(ball_identity_audit), "source_override_audit.csv")

    # ---- match table ----------------------------------------------------------------
    m = checked_merge(m, comp, "matches+competitions", on="comp_id", how="left", validate="m:1")
    pr = m.result.apply(parse_result)
    m["res_kind"] = [p[0] for p in pr]
    m["res_n"] = [p[1] for p in pr]
    m["res_dls"] = [p[2] for p in pr]
    for mid, fix in CFG["source_overrides"]["result_fixes"].items():
        sel = m.match_id == int(mid)
        assert sel.sum() == 1 and m.loc[sel, "result"].iloc[0] == fix["raw_result"], f"override {mid} no longer matches the raw data"
        m.loc[sel, "res_n"] = fix["res_n"]
        print(f"  source override applied to match {mid}: {fix['raw_result']!r} -> {fix['corrected']!r}")
    m["year"] = pd.to_datetime(m.match_date).dt.year
    m["tier"] = np.where(m.comp_name.str.startswith("IPL"), "IPL",
                         np.where(m.comp_id.isin(CFG["a_team_comp_ids"]), "A-team", "T20I"))
    m["reduced"] = (m.first_inn_revised_overs.notna() | m.second_inn_revised_overs.notna()
                    | m.revised_target.notna() | m.res_dls)
    m["has_balls"] = m.match_id.isin(b.match_id)
    fm = set(CFG["full_members"])
    m["home_assoc"] = (m.tier == "T20I") & ~m.home_team.isin(fm)
    m["away_assoc"] = (m.tier == "T20I") & ~m.away_team.isin(fm)

    # ---- delivery basics --------------------------------------------------------------
    b["et"] = b.extras_type.fillna("none")
    b["legal"] = ~b.et.isin(CFG["illegal_extras"])
    b["is_wide"] = b.et == "wide"
    b["is_noball"] = b.et.isin(CFG["noball_extras"])
    g = b.groupby(["match_id", "innings"], sort=False)
    b["legal_before"] = g.legal.cumsum() - b.legal
    b["wkts_before"] = g.is_wicket.cumsum() - b.is_wicket
    b["prev_noball"] = g.is_noball.shift(1, fill_value=False)
    b["free_hit"] = b.prev_noball.astype(bool)
    b.drop(columns="prev_noball", inplace=True)

    # ---- innings summaries ------------------------------------------------------------
    inn = g.agg(bat=("runs", "sum"), e2=("extras_2_runs", "sum"), wk=("is_wicket", "sum"),
                lb=("legal", "sum"), bat_team=("batting_team_id", "first")).reset_index()
    cnt = b.groupby(["match_id", "innings", "et"]).size().unstack(fill_value=0).reset_index()
    inn = checked_merge(inn, cnt, "innings+extras counts", on=["match_id", "innings"], how="left")
    for t in EXTRA_TYPES + ["Penalty"]:
        if t not in inn:
            inn[t] = 0
    w = inn.pivot(index="match_id", columns="innings")
    w.columns = [f"{a}_{i}" for a, i in w.columns]
    m = checked_merge(m, w.reset_index(), "matches+innings summary", on="match_id", how="left")
    m["two_innings"] = m.bat_2.notna()
    m["first_bat_won"] = m.win_team_id == m.bat_team_1
    # complete first innings: 120 legal balls or all out
    m["inn1_complete"] = (m.lb_1 == 120) | (m.wk_1 >= 10)
    m["inn2_resolved"] = np.where(m.res_kind == "runs", (m.lb_2 == 120) | (m.wk_2 >= 9),
                                  np.where(m.res_kind == "wkts", True, (m.lb_2 == 120) | (m.wk_2 >= 10)))
    m["res_consistent"] = np.where(m.res_kind == "runs", m.first_bat_won,
                                   np.where(m.res_kind == "wkts", ~m.first_bat_won & m.win_team_id.notna(), True))
    m["clean"] = (m.has_balls & m.two_innings & ~m.reduced & m.res_kind.isin(["runs", "wkts", "tie"])
                  & m.inn1_complete & m.inn2_resolved & m.res_consistent & m.win_team_id.notna())
    excl = {
        "no ball data": int((~m.has_balls).sum()),
        "reduced (revised fields or DLS text)": int((m.has_balls & m.reduced).sum()),
        "no winner (no result / abandoned) with balls, not reduced": int(
            (m.has_balls & ~m.reduced & ~m.res_kind.isin(["runs", "wkts", "tie"])).sum()),
        "first innings incomplete without flag": int(
            (m.has_balls & ~m.reduced & m.res_kind.isin(["runs", "wkts", "tie"]) & ~m.inn1_complete).sum()),
        "second innings unresolved or result inconsistent": int(
            (m.has_balls & ~m.reduced & m.res_kind.isin(["runs", "wkts", "tie"]) & m.inn1_complete
             & ~(m.inn2_resolved & m.res_consistent & m.two_innings & m.win_team_id.notna())).sum()),
    }
    for k, v in excl.items():
        print(f"  excluded matches, {k}: {v}")
    print(f"  clean matches kept for win probability and pressure analysis: {int(m.clean.sum())}")

    # ---- wicket check (exact, independent of extras) ------------------------------------
    wk = m[m.has_balls & (m.res_kind == "wkts")]
    wk_ok = (10 - wk.res_n) == wk.wk_2
    print(f"  wicket check: {int(wk_ok.sum())}/{len(wk)} chases match 'won by N wickets'")

    # ---- expanding, strictly past-only extras calibration --------------------------------
    # A match's outcome may calibrate later matches, but never its own run reconstruction or
    # any earlier match. All matches played on the same date share one parameter vintage.
    cal = m[m.clean & (m.res_kind == "runs")].copy()
    cal["calibration_date"] = pd.to_datetime(cal.match_date).dt.normalize()
    D = np.column_stack([(cal[f"{t}_1"] - cal[f"{t}_2"]).values for t in EXTRA_TYPES]).astype(float)
    y = (cal.res_n - (cal.bat_1 - cal.bat_2) - (cal.e2_1 - cal.e2_2)
         - PENALTY_RUNS * (cal.Penalty_1 - cal.Penalty_2)).values.astype(float)
    simple = np.ones(len(EXTRA_TYPES))
    min_train_matches = 40
    param_rows = []
    match_dates = pd.to_datetime(m.match_date).dt.normalize()
    for date in sorted(match_dates.dropna().unique()):
        prior = cal.calibration_date < date
        n_prior = int(prior.sum())
        if n_prior >= min_train_matches:
            v_date = l1_fit(D[prior], y[prior])
            method = "expanding_lad"
            max_prior = cal.loc[prior, "calibration_date"].max()
        else:
            v_date = simple.copy()
            method = "one_run_fallback"
            max_prior = pd.NaT
        row = dict(calibration_date=date, calibration_method=method,
                   calibration_training_matches=n_prior if method == "expanding_lad" else 0,
                   calibration_max_training_date=max_prior)
        row.update({f"run_value_{t}": float(x) for t, x in zip(EXTRA_TYPES, v_date)})
        param_rows.append(row)
    params_by_date = pd.DataFrame(param_rows)
    m["calibration_date"] = match_dates
    m = checked_merge(m, params_by_date, "matches+past-only extras calibration",
                      on="calibration_date", how="left", validate="m:1")
    for t in EXTRA_TYPES:
        m[f"run_value_{t}"] = m[f"run_value_{t}"].fillna(1.0)
    m["calibration_method"] = m.calibration_method.fillna("one_run_fallback")
    m["calibration_training_matches"] = m.calibration_training_matches.fillna(0).astype(int)
    m["calibration_max_training_date"] = pd.to_datetime(
        m.calibration_max_training_date, errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    run_value_cols = [f"run_value_{t}" for t in EXTRA_TYPES]
    extras_detail = m[["match_id", "match_date", "calibration_method", "calibration_training_matches",
                       "calibration_max_training_date"] + run_value_cols].copy()
    extras_detail.to_csv(os.path.join(TABLES, "extras_calibration_by_match.csv"),
                         index=False, float_format="%.6g")

    # Strictly out-of-time margin diagnostic: every row is scored with coefficients estimated
    # only from clean run-margin matches on earlier dates.
    cal_eval = cal.merge(extras_detail[["match_id"] + run_value_cols], on="match_id", validate="1:1")
    V_oof = cal_eval[run_value_cols].to_numpy(dtype=float)
    cv_err = (D * V_oof).sum(axis=1) - y
    simple_err = D @ simple - y
    applied_median = np.median(extras_detail[run_value_cols].to_numpy(dtype=float), axis=0)
    rows = []
    for t, fitted_value in zip(EXTRA_TYPES, applied_median):
        rows.append(dict(item=f"run value: {t}", fitted=round(float(fitted_value), 3), simple=1.0,
                         n=int(b.et.eq(t).sum())))
    rows.append(dict(item="run value: Penalty (fixed)", fitted=PENALTY_RUNS, simple=PENALTY_RUNS,
                     n=int(b.et.eq("Penalty").sum())))
    for name, err in [("fitted", cv_err), ("simple", simple_err)]:
        rows.append(dict(item=f"margin MAE (runs), {name}", fitted=np.abs(err).mean(),
                         simple=np.nan, n=len(err)))
        rows.append(dict(item=f"margin RMSE (runs), {name}", fitted=np.sqrt(np.mean(err ** 2)),
                         simple=np.nan, n=len(err)))
        rows.append(dict(item=f"exact-margin rate, {name}", fitted=np.mean(np.abs(np.round(err)) < 0.5),
                         simple=np.nan, n=len(err)))
        rows.append(dict(item=f"within 2 runs rate, {name}", fitted=np.mean(np.abs(err) <= 2.0),
                         simple=np.nan, n=len(err)))
    rows.append(dict(item="margin MAE (runs), fitted, strictly out of time", fitted=np.abs(cv_err).mean(),
                     simple=np.nan, n=len(y)))
    mae_fit = float(np.abs(cv_err).mean())
    mae_simple = float(np.abs(simple_err).mean())
    print(f"  median past-only extras values {dict(zip(EXTRA_TYPES, np.round(applied_median, 3)))}")
    print(f"  strictly past-only margin MAE {mae_fit:.3f} vs fixed 1-run rule {mae_simple:.3f}; n={len(y)}")

    val = dict(zip(EXTRA_TYPES, applied_median))
    val["Penalty"] = PENALTY_RUNS
    val["none"] = 0.0
    # Join each match's own historical calibration vintage; no same-match or future result is used.
    b = checked_merge(b, extras_detail[["match_id"] + run_value_cols], "deliveries+past-only extras values",
                      on="match_id", how="left", validate="m:1")
    b["extra_runs"] = b["extras_2_runs"].astype(float)
    for t, col in zip(EXTRA_TYPES, run_value_cols):
        b["extra_runs"] += np.where(b.et == t, b[col], 0.0)
    b["extra_runs"] += np.where(b.et == "Penalty", PENALTY_RUNS, 0.0)
    b["total_runs"] = b.runs + b.extra_runs
    # runs charged to the bowler: bat runs plus wides and no-balls (not byes, leg byes, penalties)
    b["bowler_runs"] = b.runs + np.where(b.is_wide | b.is_noball, b.extra_runs, 0.0)
    g = b.groupby(["match_id", "innings"], sort=False)
    b["score_before"] = g.total_runs.cumsum() - b.total_runs
    b["rem_runs"] = g.total_runs.transform("sum") - b.score_before
    tot = g.total_runs.sum().unstack()
    m = checked_merge(m, tot.rename(columns={1: "tot_1", 2: "tot_2"}).reset_index(),
                      "matches+reconstructed totals", on="match_id", how="left")

    # ---- chase target: reconstructed exclusively from the first innings -----------------
    # The target is a pre-chase match condition. Never infer it from the final score, margin,
    # wickets remaining, winner, or result string.
    m["target_recon"] = np.rint(m.tot_1) + 1.0
    m["target"] = m["target_recon"]
    m["target_source"] = "first_innings_ball_reconstruction"
    target_audit = m[m.clean][["match_id", "match_date", "tot_1", "target_recon", "target",
                               "target_source", "calibration_method", "calibration_training_matches",
                               "calibration_max_training_date"]].copy()
    target_audit.to_csv(os.path.join(TABLES, "target_reconstruction_by_match.csv"),
                        index=False, float_format="%.6g")
    target_summary = target_audit.groupby(["target_source", "calibration_method"]).agg(
        matches=("match_id", "nunique"), mean_reconstructed_first_innings=("tot_1", "mean"),
        mean_target=("target", "mean"), min_target=("target", "min"),
        max_target=("target", "max")).reset_index()
    save_table(target_summary, "target_reconstruction_audit.csv")
    save_table(pd.DataFrame(rows), "extras_calibration.csv")

    # ---- venue context: strictly past-date first-innings average, shrunk to past tier mean ---
    v1 = m[m.clean][["match_id", "match_date", "venue_id", "tier", "tot_1"]].copy()
    v1["match_date"] = pd.to_datetime(v1.match_date).dt.normalize()
    v1 = v1.sort_values(["match_date", "match_id"]).reset_index(drop=True)
    # Use only completed matches on strictly earlier dates. Same-day matches are one batch because
    # ball-by-ball timestamps are unavailable; no match can borrow a venue/tier average from its date.
    vd = v1.groupby(["match_date", "venue_id"], dropna=False).tot_1.agg(["sum", "count"]).reset_index()
    vd["venue_sum_prior"] = vd.groupby("venue_id", dropna=False)["sum"].cumsum() - vd["sum"]
    vd["venue_n_prior"] = vd.groupby("venue_id", dropna=False)["count"].cumsum() - vd["count"]
    td = v1.groupby(["match_date", "tier"]).tot_1.agg(["sum", "count"]).reset_index()
    td["tier_sum_prior"] = td.groupby("tier")["sum"].cumsum() - td["sum"]
    td["tier_n_prior"] = td.groupby("tier")["count"].cumsum() - td["count"]
    gd = v1.groupby("match_date").tot_1.agg(["sum", "count"]).reset_index()
    gd["global_sum_prior"] = gd["sum"].cumsum() - gd["sum"]
    gd["global_n_prior"] = gd["count"].cumsum() - gd["count"]
    v1 = v1.merge(vd[["match_date", "venue_id", "venue_sum_prior", "venue_n_prior"]],
                  on=["match_date", "venue_id"], how="left", validate="m:1")
    v1 = v1.merge(td[["match_date", "tier", "tier_sum_prior", "tier_n_prior"]],
                  on=["match_date", "tier"], how="left", validate="m:1")
    v1 = v1.merge(gd[["match_date", "global_sum_prior", "global_n_prior"]],
                  on="match_date", how="left", validate="m:1")
    global_sum = v1.global_sum_prior.to_numpy(dtype=float)
    global_n = v1.global_n_prior.to_numpy(dtype=float)
    tier_sum = v1.tier_sum_prior.to_numpy(dtype=float)
    tier_n = v1.tier_n_prior.to_numpy(dtype=float)
    global_prior = np.divide(global_sum, global_n, out=np.full(len(v1), 150.0),
                             where=global_n > 0)
    tier_prior = np.divide(tier_sum, tier_n, out=global_prior.copy(), where=tier_n > 0)
    K = 3.0
    v1["venue_avg"] = (v1.venue_sum_prior.fillna(0) + K * tier_prior) / (v1.venue_n_prior.fillna(0) + K)
    m = checked_merge(m, v1[["match_id", "venue_avg"]], "matches+past-only venue average", on="match_id", how="left")
    # Non-clean matches are excluded downstream; use the last historical estimate only as a safe fallback.
    vmean = v1.groupby("venue_id").venue_avg.mean()
    tmean = v1.groupby("tier").venue_avg.mean()
    m["venue_avg"] = m.venue_avg.fillna(m.venue_id.map(vmean)).fillna(m.tier.map(tmean)).fillna(150.0)

    # ---- attach match info to deliveries --------------------------------------------------
    keep = ["match_id", "comp_id", "match_date", "year", "tier", "venue_id", "venue_avg", "clean",
            "reduced", "win_team_id", "target", "target_recon", "target_source",
            "home_team_id", "away_team_id", "home_assoc",
            "away_assoc", "stage", "knock_out"]
    b = checked_merge(b, m[keep], "deliveries+match info", on="match_id", how="left", validate="m:1")
    b["bat_assoc"] = np.where(b.batting_team_id == b.home_team_id, b.home_assoc, b.away_assoc)
    b["bowl_assoc"] = np.where(b.bowling_team_id == b.home_team_id, b.home_assoc, b.away_assoc)
    b["bat_win"] = (b.batting_team_id == b.win_team_id).astype(float)
    b.loc[b.win_team_id.isna(), "bat_win"] = np.nan

    # ---- state before the ball -------------------------------------------------------------
    b["balls_left"] = 120 - b.legal_before
    b["over"] = b.legal_before // 6 + 1
    b["over"] = b.over.clip(upper=20)
    b["phase"] = phase_of_over(b.over)
    ob = b.legal_before / 6.0
    b["crr"] = np.where(b.legal_before > 0, b.score_before / np.maximum(ob, 1e-9), np.nan)
    b["target"] = np.where(b.innings == 2, b.target, np.nan)
    b["runs_needed"] = b.target - b.score_before
    b["rrr"] = np.where(b.innings == 2, b.runs_needed / (b.balls_left / 6.0), np.nan)
    b["rrr_gap"] = b.rrr - b.crr.fillna(b.rrr)
    # momentum over the previous 12 deliveries of the innings
    g = b.groupby(["match_id", "innings"], sort=False)
    cs_r = g.total_runs.cumsum() - b.total_runs
    cs_w = g.is_wicket.cumsum() - b.is_wicket
    b["r12_drop"] = g.total_runs.shift(12, fill_value=0.0)
    b["w12_drop"] = g.is_wicket.shift(12, fill_value=False).astype(int)
    b["runs_last12"] = cs_r - cs_r.groupby([b.match_id, b.innings]).shift(12, fill_value=0.0)
    b["wkts_last12"] = cs_w - cs_w.groupby([b.match_id, b.innings]).shift(12, fill_value=0)
    dot = (b.total_runs == 0).astype(int)
    grp_key = (b.match_id.astype(str) + "_" + b.innings.astype(str))
    reset = (dot == 0).groupby(grp_key).cumsum()
    streak_incl = dot.groupby([grp_key, reset]).cumsum()
    b["dot_streak"] = streak_incl.groupby(grp_key).shift(1, fill_value=0)

    # ---- acceptance rows ---------------------------------------------------------------------
    oc = b.groupby(["match_id", "innings", "overid"]).legal.sum()
    ic = b.groupby(["match_id", "innings"]).legal.sum()
    last_over = b.groupby(["match_id", "innings"]).overid.transform("max")
    full_over = b[b.overid < last_over].groupby(["match_id", "innings", "overid"]).legal.sum()
    acc = [
        dict(check="legal balls per completed over == 6 (share)", claimed=">= 0.999",
             observed=round(float((full_over == 6).mean()), 5),
             status="pass" if (full_over == 6).mean() >= 0.999 else "FAIL",
             note=f"{int((full_over != 6).sum())} of {len(full_over)} non-final overs differ; overs >6: {int((oc > 6).sum())}"),
        dict(check="innings with more than 120 legal balls", claimed=0, observed=int((ic > 120).sum()),
             status="pass" if (ic > 120).sum() == 0 else "FAIL", note=""),
        dict(check="complete first innings in clean matches have 120 legal balls or are all out",
             claimed=1.0, observed=float(m[m.clean].inn1_complete.mean()), status="pass", note=""),
        dict(check="wicket check: wickets lost in chase == 10 - N for 'won by N wickets'",
             claimed=1.0, observed=round(float(wk_ok.mean()), 5),
             status="pass" if wk_ok.all() else "FAIL",
             note=f"{int(wk_ok.sum())}/{len(wk)} matches; one result string corrected from an outside source (D-24)"),
        dict(check="extras calibration strictly past-only", claimed="training dates strictly earlier than scored match",
             observed=bool((pd.to_datetime(extras_detail.loc[extras_detail.calibration_training_matches > 0,
                          "calibration_max_training_date"]) <
                            pd.to_datetime(extras_detail.loc[extras_detail.calibration_training_matches > 0,
                          "match_date"])).all()),
             status="pass" if (pd.to_datetime(extras_detail.loc[extras_detail.calibration_training_matches > 0,
                          "calibration_max_training_date"]) <
                               pd.to_datetime(extras_detail.loc[extras_detail.calibration_training_matches > 0,
                          "match_date"])).all() else "FAIL",
             note=f"expanding LAD; one-run fallback before {min_train_matches} prior clean run-margin matches"),
    ]
    for k, vv in excl.items():
        acc.append(dict(check=f"matches excluded: {k}", claimed="", observed=vv, status="info", note=""))
    acc.append(dict(check="clean matches kept", claimed="", observed=int(m.clean.sum()), status="info", note=""))
    acc.append(dict(check="deliveries in clean matches (innings 1-2)", claimed="", observed=int(b.clean.sum()),
                    status="info", note=f"of {len(b)} innings 1-2 deliveries"))
    dq = pd.read_csv(os.path.join(TABLES, "data_quality.csv"))
    dq = dq[dq.stage != "02_build_state"]
    dq = pd.concat([dq, pd.DataFrame(acc).assign(stage="02_build_state")], ignore_index=True)
    save_table(dq, "data_quality.csv")

    b.to_parquet(os.path.join(INTERIM, "balls.parquet"), index=False)
    m.to_parquet(os.path.join(INTERIM, "match_info.parquet"), index=False)
    pd.Series(val).to_json(os.path.join(INTERIM, "extras_values.json"))
    print(f"  wrote balls.parquet ({len(b)} rows), match_info.parquet ({len(m)} rows)")


if __name__ == "__main__":
    main()
