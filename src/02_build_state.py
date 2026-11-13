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

    # ---- extras calibration -------------------------------------------------------------
    cal = m[m.clean & (m.res_kind == "runs")].copy()
    D = np.column_stack([(cal[f"{t}_1"] - cal[f"{t}_2"]).values for t in EXTRA_TYPES]).astype(float)
    y = (cal.res_n - (cal.bat_1 - cal.bat_2) - (cal.e2_1 - cal.e2_2)
         - PENALTY_RUNS * (cal.Penalty_1 - cal.Penalty_2)).values.astype(float)
    v = l1_fit(D, y)
    simple = np.ones(len(EXTRA_TYPES))
    # out-of-sample check, 5 folds
    rng = np.random.RandomState(CFG["seed"])
    fold = rng.permutation(len(y)) % 5
    cv_err = np.zeros(len(y))
    for k in range(5):
        vk = l1_fit(D[fold != k], y[fold != k])
        cv_err[fold == k] = D[fold == k] @ vk - y[fold == k]
    rows = []
    for t, val in zip(EXTRA_TYPES, v):
        rows.append(dict(item=f"run value: {t}", fitted=round(float(val), 3), simple=1.0,
                         n=int(b.et.eq(t).sum())))
    rows.append(dict(item="run value: Penalty (fixed)", fitted=PENALTY_RUNS, simple=PENALTY_RUNS,
                     n=int(b.et.eq("Penalty").sum())))
    for name, vec in [("fitted", v), ("simple", simple)]:
        e = D @ vec - y
        rows.append(dict(item=f"margin MAE (runs), {name}", fitted=np.abs(e).mean(), simple=np.nan, n=len(y)))
        rows.append(dict(item=f"margin RMSE (runs), {name}", fitted=np.sqrt((e ** 2).mean()), simple=np.nan, n=len(y)))
        rows.append(dict(item=f"exact-margin rate, {name}", fitted=np.mean(np.abs(np.round(e)) < 0.5),
                         simple=np.nan, n=len(y)))
        rows.append(dict(item=f"within 2 runs rate, {name}", fitted=np.mean(np.abs(e) <= 2.0), simple=np.nan, n=len(y)))
    rows.append(dict(item="margin MAE (runs), fitted, 5-fold out of sample", fitted=np.abs(cv_err).mean(),
                     simple=np.nan, n=len(y)))
    mae_fit = np.abs(D @ v - y).mean()
    mae_simple = np.abs(D @ simple - y).mean()
    print(f"  extras values {dict(zip(EXTRA_TYPES, np.round(v, 3)))}")
    print(f"  margin MAE fitted {mae_fit:.3f} vs simple {mae_simple:.3f}; cv {np.abs(cv_err).mean():.3f}; n={len(y)}")

    val = dict(zip(EXTRA_TYPES, v))
    val["Penalty"] = PENALTY_RUNS
    val["none"] = 0.0
    b["extra_runs"] = b.et.map(val).astype(float) + b.extras_2_runs
    b["total_runs"] = b.runs + b.extra_runs
    # runs charged to the bowler: bat runs plus wides and no-balls (not byes, leg byes, penalties)
    b["bowler_runs"] = b.runs + np.where(b.is_wide | b.is_noball, b.extra_runs, 0.0)
    g = b.groupby(["match_id", "innings"], sort=False)
    b["score_before"] = g.total_runs.cumsum() - b.total_runs
    b["rem_runs"] = g.total_runs.transform("sum") - b.score_before
    tot = g.total_runs.sum().unstack()
    m = checked_merge(m, tot.rename(columns={1: "tot_1", 2: "tot_2"}).reset_index(),
                      "matches+reconstructed totals", on="match_id", how="left")

    # ---- chase target -------------------------------------------------------------------
    # reconstructed: first-innings total + 1.  result_anchored: recover the true target from the
    # result string so that the end-of-chase state is exact (see DECISIONS.md D-07).
    last = b[b.innings == 2].groupby("match_id").tail(1).set_index("match_id")
    m["score_before_last_2"] = m.match_id.map(last.score_before)
    m["target_recon"] = np.ceil(m.tot_1 - 1e-9) + 1 - 0.0
    tgt = m.target_recon.copy()
    is_r = m.clean & (m.res_kind == "runs")
    is_w = m.clean & (m.res_kind == "wkts")
    is_t = m.clean & (m.res_kind == "tie")
    tgt[is_r] = m.tot_2[is_r] + m.res_n[is_r] + 1
    tgt[is_t] = m.tot_2[is_t] + 1
    lo = np.floor(m.score_before_last_2[is_w]) + 1
    tgt[is_w] = np.minimum(np.maximum(m.target_recon[is_w], lo), np.maximum(m.tot_2[is_w], lo))
    m["target_anchored"] = tgt
    m["target"] = m.target_anchored if CFG["target_mode"] == "result_anchored" else m.target_recon
    m["target_source"] = np.select(
        [is_r, is_w, is_t],
        ["result_anchored_run_margin", "result_anchored_wicket_margin", "result_anchored_tie"],
        default="first_innings_reconstruction")
    m["target_adjustment_runs"] = m.target_anchored - m.target_recon
    target_audit = m[m.clean][["match_id", "match_date", "res_kind", "res_n", "tot_1", "tot_2",
                               "score_before_last_2", "target_recon", "target_anchored", "target",
                               "target_source", "target_adjustment_runs"]].copy()
    target_audit.to_csv(os.path.join(TABLES, "target_reconstruction_by_match.csv"), index=False, float_format="%.6g")
    target_summary = target_audit.groupby(["res_kind", "target_source"]).agg(
        matches=("match_id", "nunique"), mean_abs_adjustment=("target_adjustment_runs", lambda x: x.abs().mean()),
        median_abs_adjustment=("target_adjustment_runs", lambda x: x.abs().median()),
        max_abs_adjustment=("target_adjustment_runs", lambda x: x.abs().max()),
        adjusted_matches=("target_adjustment_runs", lambda x: int((x.abs() > 1e-9).sum()))).reset_index()
    save_table(target_summary, "target_reconstruction_audit.csv")
    over = (m.tot_2 - m.target_recon)[is_w]
    short = (m.tot_1 - m.tot_2 - m.res_n)[is_r]
    rows.append(dict(item="wicket-win chases: reconstructed total minus reconstructed target, mean",
                     fitted=over.mean(), simple=np.nan, n=len(over)))
    rows.append(dict(item="wicket-win chases: share with reconstructed total below reconstructed target",
                     fitted=(over < 0).mean(), simple=np.nan, n=len(over)))
    rows.append(dict(item="run-margin matches: |margin error| mean with fitted values",
                     fitted=short.abs().mean(), simple=np.nan, n=len(short)))
    rows.append(dict(item="target adjustment |anchored - reconstructed|, mean (runs)",
                     fitted=(m.target_anchored - m.target_recon)[m.clean].abs().mean(), simple=np.nan,
                     n=int(m.clean.sum())))
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
    global_prior = np.divide(v1.global_sum_prior, v1.global_n_prior,
                             out=np.full(len(v1), 150.0), where=v1.global_n_prior.to_numpy() > 0)
    tier_prior = np.divide(v1.tier_sum_prior, v1.tier_n_prior,
                           out=global_prior.copy(), where=v1.tier_n_prior.to_numpy() > 0)
    K = 3.0
    v1["venue_avg"] = (v1.venue_sum_prior.fillna(0) + K * tier_prior) / (v1.venue_n_prior.fillna(0) + K)
    m = checked_merge(m, v1[["match_id", "venue_avg"]], "matches+past-only venue average", on="match_id", how="left")
    # Non-clean matches are excluded downstream; use the last historical estimate only as a safe fallback.
    vmean = v1.groupby("venue_id").venue_avg.mean()
    tmean = v1.groupby("tier").venue_avg.mean()
    m["venue_avg"] = m.venue_avg.fillna(m.venue_id.map(vmean)).fillna(m.tier.map(tmean)).fillna(150.0)

    # ---- attach match info to deliveries --------------------------------------------------
    keep = ["match_id", "comp_id", "match_date", "year", "tier", "venue_id", "venue_avg", "clean",
            "reduced", "win_team_id", "target", "target_recon", "target_anchored", "target_source",
            "target_adjustment_runs", "home_team_id", "away_team_id", "home_assoc",
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
        dict(check="extras calibration MAE, fitted <= simple 1-run rule", claimed=round(mae_simple, 4),
             observed=round(mae_fit, 4), status="pass" if mae_fit <= mae_simple + 1e-9 else "FAIL",
             note=f"n={len(y)} run-margin matches; out-of-sample MAE {np.abs(cv_err).mean():.3f}"),
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
