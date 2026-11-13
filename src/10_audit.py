"""Stage 10: audit tables (phase 2a). Scorecards of 10 seeded random matches against their result
strings, integrity counts for joins and identities, and a leakage checklist.
Outputs: audit_scorecards.csv, audit_integrity.csv"""
import os

import numpy as np
import pandas as pd

from common import CFG, INTERIM, PROCESSED, SEED, raw, save_table


def main():
    print("Stage 10: audit")
    b = pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))
    m = pd.read_parquet(os.path.join(INTERIM, "match_info.parquet"))
    bat = pd.read_parquet(os.path.join(PROCESSED, "bat_credit.parquet"))
    bowl = pd.read_parquet(os.path.join(PROCESSED, "bowl_credit.parquet"))
    pe = raw("playing_eleven")
    teams = raw("teams").drop_duplicates("team_id").set_index("team_id").team_name

    # ---- scorecards -------------------------------------------------------------------------------
    rng = np.random.RandomState(SEED)
    ids = rng.choice(np.sort(m[m.has_balls & m.two_innings & (m.res_kind != "none")].match_id.values), 10, replace=False)
    rows = []
    for r in m[m.match_id.isin(ids)].sort_values("match_date").itertuples():
        ov = lambda lb: f"{int(lb // 6)}.{int(lb % 6)}"
        first, second = teams[r.bat_team_1], teams[r.bat_team_2]
        if r.res_kind == "wkts":
            implied = f"{second} won by {int(10 - r.wk_2)} wickets"
            ok = (10 - r.wk_2 == r.res_n) and (r.win_team_id == r.bat_team_2)
            err = np.nan
        elif r.res_kind == "runs":
            implied = f"{first} won by {r.tot_1 - r.tot_2:.0f} runs"
            ok = (r.win_team_id == r.bat_team_1) and (r.tot_1 > r.tot_2 or r.reduced)
            err = (r.tot_1 - r.tot_2) - r.res_n
        else:
            implied, ok, err = "n/a", True, np.nan
        rows.append(dict(match_id=r.match_id, date=r.match_date, result_string=r.result,
                         innings1=f"{first} {r.tot_1:.0f}/{int(r.wk_1)} ({ov(r.lb_1)} ov)",
                         innings2=f"{second} {r.tot_2:.0f}/{int(r.wk_2)} ({ov(r.lb_2)} ov)",
                         reconstructed_result=implied, winner_and_wickets_agree=bool(ok),
                         run_margin_error=err, reduced_or_excluded=bool(not r.clean),
                         target_used=r.target))
    sc = pd.DataFrame(rows)
    save_table(sc, "audit_scorecards.csv")
    print(sc[["match_id", "result_string", "innings1", "innings2", "reconstructed_result", "winner_and_wickets_agree", "run_margin_error"]].to_string())

    # ---- integrity ----------------------------------------------------------------------------------
    key = ["match_id", "innings", "innings_ball_num"]
    clean = b[b.clean]
    pt = pe.drop_duplicates(["match_id", "player_id"]).set_index(["match_id", "player_id"]).team_id
    st = pd.MultiIndex.from_arrays([clean.match_id, clean.striker_id])
    bw = pd.MultiIndex.from_arrays([clean.match_id, clean.bowler_id])
    s_team, b_team = pt.reindex(st).values, pt.reindex(bw).values
    wp = pd.read_parquet(os.path.join(INTERIM, "wp.parquet"))
    chk = [
        ("duplicate deliveries (match, innings, ball number)", int(b.duplicated(key).sum()), 0),
        ("deliveries from innings 3-4 (super overs) kept", int((b.innings > 2).sum()), 0),
        ("deliveries from reduced or unusable matches in credit tables",
         int(bat.match_id.isin(m[~m.clean].match_id).sum() + bowl.match_id.isin(m[~m.clean].match_id).sum()), 0),
        ("batting team is neither home nor away team", int(((b.batting_team_id != b.home_team_id) & (b.batting_team_id != b.away_team_id)).sum()), 0),
        ("same team bats in both innings", int((b.groupby(["match_id", "innings"]).batting_team_id.first().unstack().pipe(lambda x: x[1] == x[2])).sum()), 0),
        ("striker listed for the other team in playing_eleven", int((pd.notna(s_team) & (s_team != clean.batting_team_id.values)).sum()), 0),
        ("bowler listed for the other team in playing_eleven", int((pd.notna(b_team) & (b_team != clean.bowling_team_id.values)).sum()), 0),
        ("striker absent from playing_eleven (info only)", int(pd.isna(s_team).sum()), None),
        ("duplicate rows in playing_eleven (info only)", int(pe.duplicated(["match_id", "team_id", "player_id"]).sum()), None),
        ("striker equals non-striker (info only)", int((b.striker_id == b.non_striker_id).sum()), None),
        ("duplicate faced-ball records in batter credit", int(bat[bat.faced == 1].duplicated(key).sum()), 0),
        ("duplicate slots in bowler credit", int(bowl.duplicated(["match_id", "innings", "slot"] if "slot" in bowl else key).sum()), 0),
        ("wides counted as balls faced", int(bat[bat.faced == 1].merge(clean[clean.is_wide][key], on=key).shape[0]), 0),
        ("run outs or retired outs credited to a bowler",
         int(bowl.wkt.sum() - (clean.is_wicket & clean.dismissal_type.isin(CFG["bowler_wickets"])).sum()), 0),
        ("batter dismissed more than once in an innings", int((bat.groupby(["match_id", "innings", "player_id"]).out.sum() > 1).sum()), 0),
        ("innings with more than 10 wickets", int((b.groupby(["match_id", "innings"]).is_wicket.sum() > 10).sum()), 0),
        ("matches whose deliveries sit in more than one CV fold", int((wp.groupby("match_id").fold.nunique() > 1).sum()), 0),
        ("player ids with more than one name", int((raw("competition_team_player_mapping").groupby("player_id").player_name.nunique() > 1).sum()), 0),
        ("bowler with more than 24 legal balls in an innings (info only)", int((bowl.groupby(["match_id", "innings", "player_id"]).size() > 24).sum()), None),
    ]
    it = pd.DataFrame(chk, columns=["check", "observed", "expected"])
    it["status"] = np.where(it.expected.isna(), "info", np.where(it.observed == it.expected, "pass", "FAIL"))

    # Drill down the informational XI anomalies so they can be reconciled against source records.
    missing = clean.loc[pd.isna(s_team), ["match_id", "match_date", "comp_id", "striker_id", "batting_team_id"]].copy()
    missing = missing.rename(columns={"striker_id": "player_id", "batting_team_id": "expected_team_id"})
    missing = missing.groupby(["match_id", "match_date", "comp_id", "player_id", "expected_team_id"]).size() \
        .rename("missing_striker_balls").reset_index()
    mapping = raw("competition_team_player_mapping")
    player_map = mapping.drop_duplicates("player_id")[["player_id", "player_name"]]
    missing = missing.merge(player_map, on="player_id", how="left", validate="m:1")
    roster_teams = (mapping.groupby(["comp_id", "player_id"]).team_id
                    .agg(lambda s: tuple(sorted(set(int(x) for x in s.dropna())))).rename("mapping_team_ids")
                    .reset_index())
    missing = missing.merge(roster_teams, on=["comp_id", "player_id"], how="left", validate="m:1")
    missing["mapping_team_ids"] = missing.mapping_team_ids.apply(lambda x: x if isinstance(x, tuple) else tuple())
    missing["mapping_team_agrees"] = missing.apply(
        lambda r: int(r.expected_team_id) in r.mapping_team_ids, axis=1)
    missing["resolution"] = np.where(missing.mapping_team_agrees,
        "raw playing_eleven omission; player and team corroborated by competition roster",
        "unresolved: competition roster does not corroborate delivery team")
    missing["expected_team_name"] = missing.expected_team_id.map(teams)
    save_table(missing, "playing_eleven_missing_strikers.csv")
    unresolved_missing = int((~missing.mapping_team_agrees).sum())
    it.loc[len(it)] = ["missing XI striker references unresolved by competition roster",
                       unresolved_missing, 0, "pass" if unresolved_missing == 0 else "FAIL"]

    dup = pe[pe.duplicated(["match_id", "team_id", "player_id"], keep=False)].copy()
    if len(dup):
        dup["duplicate_group_rows"] = dup.groupby(["match_id", "team_id", "player_id"]).player_id.transform("size")
        dup["team_assignments_for_player"] = dup.groupby(["match_id", "player_id"]).team_id.transform("nunique")
        dup = dup.merge(player_map, on="player_id", how="left", validate="m:1")
        dup["team_name"] = dup.team_id.map(teams)
    save_table(dup, "playing_eleven_duplicates.csv")
    cross_team_dup_groups = (dup[dup.team_assignments_for_player > 1]
                             .groupby(["match_id", "player_id"]).ngroups if len(dup) else 0)
    it.loc[len(it)] = ["duplicate XI memberships assigned to multiple teams",
                       int(cross_team_dup_groups), 0,
                       "pass" if cross_team_dup_groups == 0 else "FAIL"]

    # Detail the two remaining source-level edge cases so they can be inspected, not merely counted.
    same_ids = b[b.striker_id == b.non_striker_id].copy()
    if len(same_ids):
        same_ids = same_ids[["match_id", "match_date", "innings", "innings_ball_num",
                             "striker_id", "non_striker_id", "batting_team_id"]]
        same_ids = same_ids.merge(player_map, left_on="striker_id", right_on="player_id",
                                  how="left", validate="m:1").drop(columns="player_id")
    save_table(same_ids, "striker_non_striker_identity_collisions.csv")

    over_limit = (bowl.groupby(["match_id", "innings", "player_id"])
                  .agg(legal_balls=("player_id", "size"), match_date=("match_date", "first"),
                       comp_id=("comp_id", "first"), team_id=("team_id", "first"),
                       overs=("over", lambda s: tuple(sorted(set(int(x) for x in s.dropna())))))
                  .reset_index())
    over_limit = over_limit[over_limit.legal_balls > 24].merge(
        player_map, on="player_id", how="left", validate="m:1")
    save_table(over_limit, "bowler_over_limit.csv")
    print(it.to_string())
    save_table(it, "audit_integrity.csv")
    assert not (it.status == "FAIL").any()


if __name__ == "__main__":
    main()
