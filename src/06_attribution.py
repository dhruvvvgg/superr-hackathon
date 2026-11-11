"""Stage 06: ball-level credit for batters and bowlers.

Batter NRAE = (bat runs - xRuns) - wicket value * (dismissed - xWkt) on balls faced.
  Dismissals are charged to dismissed_player_id: run outs of the non-striker and dismissals off
  wides become dismissal-only records (no ball faced). Retired out carries no cost.
Bowler NRAE = (xRuns - runs charged) + wicket value * (bowler wicket - xWkt) per legal-ball slot.
WPA = change in out-of-fold win probability, to the striker; the bowler gets the negative.

Outputs: data/processed/bat_credit.parquet, data/processed/bowl_credit.parquet
"""
import os

import numpy as np
import pandas as pd

from common import CFG, INTERIM, PROCESSED, checked_merge

FLAGS = ["pA", "pB", "pC", "pD", "pE", "pF"]
META = ["match_id", "innings", "innings_ball_num", "match_date", "year", "tier", "venue_id", "comp_id",
        "batting_team_id", "bowling_team_id", "over", "phase", "balls_left", "wkts_before", "pace_or_spin",
        "bowling_type", "batting_type", "batting_order", "stage", "knock_out", "pscore", "ptier", "leverage",
        "wp_before", "bat_assoc", "bowl_assoc", "fold"] + FLAGS


def main():
    print("Stage 06: attribution")
    bat = pd.read_parquet(os.path.join(INTERIM, "bat_rows.parquet"))
    bowl = pd.read_parquet(os.path.join(INTERIM, "bowl_rows.parquet"))
    balls = pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))
    balls = balls[balls.clean]
    ex = pd.read_parquet(os.path.join(INTERIM, "ball_extras.parquet"))
    pr = pd.read_parquet(os.path.join(INTERIM, "pressure.parquet"))
    key = ["match_id", "innings", "innings_ball_num"]

    # ---- batters: faced deliveries -------------------------------------------------------------
    f = bat[META + ["striker_id", "bowler_id", "runs", "is_four", "is_six", "x_runs", "x_wkt", "wkt_value",
                    "striker_out", "wpa"]].copy()
    f = f.rename(columns={"striker_id": "player_id", "bowler_id": "opp_id"})
    f["out"] = f.striker_out.astype(int)
    f["faced"] = 1
    f["nrae_runs"] = f.runs - f.x_runs
    f["nrae_wkt"] = -f.wkt_value * (f.out - f.x_wkt)
    f["nrae"] = f.nrae_runs + f.nrae_wkt
    f = f.drop(columns="striker_out")

    # ---- batters: dismissal-only records ---------------------------------------------------------
    full = checked_merge(balls, ex, "deliveries+wicket flags", on=key, how="left", validate="1:1")
    full = checked_merge(full, pr, "deliveries+pressure", on=key, how="left", validate="1:1")
    w = full[full.wkt_cost & full.dismissed_player_id.notna()].copy()
    ns = w[(w.dismissed_player_id != w.striker_id) & ~w.is_wide]     # non-striker out on a faced ball
    wd = w[w.is_wide]                                                 # anyone out off a wide
    d = pd.concat([ns.assign(kind="non-striker"), wd.assign(kind="wide")])
    do = d[META + ["bowler_id", "wkt_value"]].copy().rename(columns={"bowler_id": "opp_id"})
    do["player_id"] = d.dismissed_player_id.astype(int).values
    do["runs"] = 0; do["is_four"] = False; do["is_six"] = False
    do["x_runs"] = 0.0; do["x_wkt"] = 0.0
    do["out"] = 1; do["faced"] = 0
    do["wpa"] = np.where(d.kind == "wide", d.wpa, 0.0)   # the striker already holds the WPA of faced balls
    do["nrae_runs"] = 0.0
    do["nrae_wkt"] = -do.wkt_value
    do["nrae"] = do.nrae_wkt
    # the dismissed non-striker's batting hand is unknown on that row; blank it
    do["batting_type"] = None
    print(f"  dismissal-only records: {len(ns)} non-striker dismissals, {len(wd)} dismissals off wides")
    batc = pd.concat([f, do[f.columns]], ignore_index=True)

    n_wkt_cost = int(full.wkt_cost.sum())
    n_charged = int(batc.out.sum())
    n_ro_bowler = int((full.is_wicket & full.dismissal_type.eq("RunOut") & full.bowler_wkt).sum())
    print(f"  batter dismissals charged: {n_charged} of {n_wkt_cost} costed wickets "
          f"({int(full.is_wicket.sum()) - n_wkt_cost} retired out carry no cost; "
          f"{n_wkt_cost - n_charged} with no dismissed player id)")
    assert n_charged == int((full.wkt_cost & full.dismissed_player_id.notna()).sum())
    assert int((batc.faced == 1).sum()) == int((~full.is_wide).sum()), "wides must not count as balls faced"
    assert n_ro_bowler == 0, "run outs must not be credited to bowlers"

    # ---- bowlers: slots --------------------------------------------------------------------------------
    s = bowl[META + ["bowler_id", "striker_id", "bowler_runs", "bowler_wkt", "x_runs", "x_wkt", "wkt_value",
                     "wpa", "n_deliveries"]].copy()
    s = s.rename(columns={"bowler_id": "player_id", "striker_id": "opp_id"})
    s["wkt"] = s.bowler_wkt.astype(int)
    s["nrae_runs"] = s.x_runs - s.bowler_runs
    s["nrae_wkt"] = s.wkt_value * (s.wkt - s.x_wkt)
    s["nrae"] = s.nrae_runs + s.nrae_wkt
    s["wpa"] = -s.wpa
    s = s.drop(columns="bowler_wkt")
    assert int(s.wkt.sum()) == int(full.bowler_wkt.sum())
    print(f"  bowler wickets credited: {int(s.wkt.sum())} of {int(full.is_wicket.sum())} wickets "
          f"(run outs {int(full.dismissal_type.eq('RunOut').sum())} not credited)")

    # ---- weights and keys -------------------------------------------------------------------------------
    ref = pd.Timestamp(CFG["reference_date"])
    W = CFG["weights"]
    for t, own, opp_assoc in [(batc, "batting_team_id", "bowl_assoc"), (s, "bowling_team_id", "bat_assoc")]:
        months = (ref - pd.to_datetime(t.match_date)).dt.days / 30.4375
        t["months_back"] = months
        t["w_recency"] = 0.5 ** (months / W["recency_half_life_months"])
        t["opp_assoc"] = t[opp_assoc].astype(bool)
        t["w_comp"] = np.select([t.tier == "A-team", (t.tier == "T20I") & t.opp_assoc, t.tier == "T20I"],
                                [W["a_team"], W["t20i_associate_opposition"], W["t20i_full_member_opposition"]],
                                default=W["ipl"])
        t["team_id"] = t[own]
        t["team_season"] = t[own].astype(str) + "_" + t.year.astype(str)
        other = "bowling_team_id" if own == "batting_team_id" else "batting_team_id"
        t["opp_team_season"] = t[other].astype(str) + "_" + t.year.astype(str)
    batc["player_id"] = batc.player_id.astype(int)
    print(f"  batter records: {len(batc)} ({int(batc.faced.sum())} faced); bowler slots: {len(s)}")
    print(f"  mean NRAE per ball: batters {batc[batc.faced == 1].nrae.mean():+.4f}, bowlers {s.nrae.mean():+.4f}")
    batc.to_parquet(os.path.join(PROCESSED, "bat_credit.parquet"), index=False)
    s.to_parquet(os.path.join(PROCESSED, "bowl_credit.parquet"), index=False)


if __name__ == "__main__":
    main()
