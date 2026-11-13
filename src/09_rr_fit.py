"""Stage 09: Rajasthan Royals fit layer for the IPL 2027 auction.

Kept separate from the Unstop rankings: this stage only reads the ratings and adds context.
Outputs: rr_team_profile.csv, rr_incumbents.csv, rr_fit.csv, figure rr_gap.png
"""
import os

import numpy as np
import pandas as pd

from common import CFG, PROCESSED, TABLES, FIGURES, raw, player_names, save_table, setup_matplotlib

RR = CFG["rr_team_id"]
AVAIL = "unknown, check after retention list"


def per100(s):
    return 100 * s.mean() if len(s) else np.nan


def bat_role(pos):
    return "opener" if pos <= 2 else ("top/middle order (3-4)" if pos <= 4 else "middle order/finisher (5+)")


def bowl_role(pace, death_share, pp_share):
    if pace != "Pace":
        return "spinner"
    return "pace, death-leaning" if death_share >= 0.30 else ("pace, powerplay-leaning" if pp_share >= 0.45 else "pace, all phases")


def main(rating_dir=None, out_dir=None, bat_credit_name="bat_credit", bowl_credit_name="bowl_credit",
         figure_path=None, label="Stage 09"):
    rating_dir = rating_dir or TABLES
    out_dir = out_dir or TABLES
    figure_path = figure_path or os.path.join(FIGURES, "rr_gap.png")
    os.makedirs(out_dir, exist_ok=True)
    print(f"{label}: RR fit")
    names = player_names()
    bat = pd.read_parquet(os.path.join(PROCESSED, f"{bat_credit_name}.parquet"))
    bowl = pd.read_parquet(os.path.join(PROCESSED, f"{bowl_credit_name}.parquet"))
    rat = {"batter": pd.read_csv(os.path.join(rating_dir, "ratings_batters.csv" if rating_dir.endswith("v3") else "batter_ratings.csv")),
           "bowler": pd.read_csv(os.path.join(rating_dir, "ratings_bowlers.csv" if rating_dir.endswith("v3") else "bowler_ratings.csv"))}
    mp = raw("competition_team_player_mapping")
    pe = raw("playing_eleven")
    m = raw("matches")

    # ---- 1. RR team pressure profile, IPL 2025 and 2026 -------------------------------------------------
    rows = []
    for disc, d in [("batting", bat[bat.faced == 1]), ("bowling", bowl)]:
        ipl = d[(d.tier == "IPL") & d.year.isin([2025, 2026])]
        for yr in (2025, 2026):
            y = ipl[ipl.year == yr]
            for situ, s in [("setting" if disc == "batting" else "defending", y[y.innings == (1 if disc == "batting" else 2)]),
                            ("chasing" if disc == "batting" else "bowling first", y[y.innings == (2 if disc == "batting" else 1)]),
                            ("all", y)]:
                for ph in ["powerplay", "middle", "death", "all"]:
                    c = s if ph == "all" else s[s.phase == ph]
                    for samp, cc in [("pressure", c[c.pA]), ("all balls", c)]:
                        team = cc.groupby("team_id").agg(nrae100=("nrae", per100), balls=("nrae", "size"), wpa=("wpa", "sum"))
                        if RR not in team.index:
                            continue
                        rk = team.nrae100.rank(ascending=False)
                        rows.append(dict(discipline=disc, year=yr, situation=situ, phase=ph, sample=samp,
                                         rr_nrae_per100=team.loc[RR, "nrae100"], rr_balls=int(team.loc[RR, "balls"]),
                                         league_mean_nrae_per100=per100(cc.nrae), rr_rank_of_teams=int(rk[RR]),
                                         n_teams=len(team), rr_wpa_total=team.loc[RR, "wpa"]))
    prof = pd.DataFrame(rows)
    prof["rr_minus_league"] = prof.rr_nrae_per100 - prof.league_mean_nrae_per100
    prof.to_csv(os.path.join(out_dir, "rr_team_profile.csv"), index=False, float_format="%.6g")
    key = prof[(prof["sample"] == "pressure") & (prof.situation == "all") & (prof.phase != "all")]
    print(key[["discipline", "year", "phase", "rr_nrae_per100", "rr_balls", "rr_rank_of_teams", "rr_minus_league"]].round(1).to_string())
    gaps = key[key.year == 2026].sort_values("rr_minus_league")
    gap_cells = [(r.discipline, r.phase) for r in gaps.itertuples() if r.rr_rank_of_teams >= 7]
    print("  RR 2026 pressure gap cells (rank 7 or worse of 10):", gap_cells)

    # ---- player usage profiles ----------------------------------------------------------------------------------
    def bat_profile(pid):
        g = bat[(bat.player_id == pid) & (bat.faced == 1)]
        p = g[g.pA]
        pos = g.groupby("match_id").batting_order.first().median()
        r = dict(role=bat_role(pos), median_batting_position=pos, hand=g.batting_type.mode().iloc[0],
                 share_powerplay=(g.phase == "powerplay").mean(), share_middle=(g.phase == "middle").mean(),
                 share_death=(g.phase == "death").mean(),
                 press_sr_vs_pace=100 * p[p.pace_or_spin == "Pace"].runs.mean(), press_balls_vs_pace=int((p.pace_or_spin == "Pace").sum()),
                 press_sr_vs_spin=100 * p[p.pace_or_spin == "Spin"].runs.mean(), press_balls_vs_spin=int((p.pace_or_spin == "Spin").sum()),
                 press_nrae100_vs_pace=per100(p[p.pace_or_spin == "Pace"].nrae), press_nrae100_vs_spin=per100(p[p.pace_or_spin == "Spin"].nrae))
        return r, g, p

    def bowl_profile(pid):
        g = bowl[bowl.player_id == pid]
        p = g[g.pA]
        pace = g.pace_or_spin.mode().iloc[0]
        r = dict(role=bowl_role(pace, (g.phase == "death").mean(), (g.phase == "powerplay").mean()),
                 pace_or_spin=pace, bowling_type=g.bowling_type.mode().iloc[0],
                 share_powerplay=(g.phase == "powerplay").mean(), share_middle=(g.phase == "middle").mean(),
                 share_death=(g.phase == "death").mean(),
                 press_econ_vs_rhb=6 * p[p.batting_type == "RHB"].bowler_runs.mean(), press_balls_vs_rhb=int((p.batting_type == "RHB").sum()),
                 press_econ_vs_lhb=6 * p[p.batting_type == "LHB"].bowler_runs.mean(), press_balls_vs_lhb=int((p.batting_type == "LHB").sum()),
                 press_nrae100_vs_rhb=per100(p[p.batting_type == "RHB"].nrae), press_nrae100_vs_lhb=per100(p[p.batting_type == "LHB"].nrae))
        return r, g, p

    def common(p):
        return dict(press_nrae100_2022_24=per100(p[p.year <= 2024].nrae), press_balls_2022_24=int((p.year <= 2024).sum()),
                    press_nrae100_2025_26=per100(p[p.year >= 2025].nrae), press_balls_2025_26=int((p.year >= 2025).sum()),
                    press_nrae100_ipl=per100(p[p.tier == "IPL"].nrae), press_balls_ipl=int((p.tier == "IPL").sum()),
                    press_nrae100_t20i=per100(p[p.tier == "T20I"].nrae), press_balls_t20i=int((p.tier == "T20I").sum()))

    # ---- RR incumbents (IPL 2026 squad) ---------------------------------------------------------------------------
    squad = mp[(mp.comp_id == CFG["ipl_comp_ids"]["2026"]) & (mp.team_id == RR)][["player_id", "player_name"]]
    px = pe.merge(m[["match_id", "comp_id"]], on="match_id", how="left", validate="m:1")
    px = px[(px.comp_id == CFG["ipl_comp_ids"]["2026"]) & (px.team_id == RR) & px.is_played]
    apps = px.groupby("player_id").match_id.nunique()
    nat = mp[~mp.comp_name.str.startswith("IPL") & ~mp.team_name.str.endswith(" A")].groupby("player_id").team_name \
        .agg(lambda s: s.value_counts().index[0])
    inc = []
    for r in squad.itertuples():
        row = dict(player_id=r.player_id, player_name=r.player_name, ipl2026_matches=int(apps.get(r.player_id, 0)),
                   national_team=nat.get(r.player_id, "none in data (uncapped)"))
        row["overseas_derived"] = row["national_team"] not in ("India", "none in data (uncapped)")
        for label, prof_fn, tab in [("batter", bat_profile, bat), ("bowler", bowl_profile, bowl)]:
            g26 = tab[(tab.player_id == r.player_id) & (tab.tier == "IPL") & (tab.year == 2026) & (tab.team_id == RR)]
            n26 = int((g26.faced == 1).sum()) if label == "batter" else len(g26)
            row[f"{label}_balls_ipl2026"] = n26
            rr_ = rat[label][rat[label].player_id == r.player_id]
            row[f"{label}_eligible"] = bool(len(rr_))
            row[f"{label}_rank"] = rr_["rank"].iloc[0] if len(rr_) else np.nan
            row[f"{label}_rating"] = rr_.rating.iloc[0] if len(rr_) else np.nan
            row[f"{label}_role"] = prof_fn(r.player_id)[0]["role"] if (tab.player_id == r.player_id).any() and n26 >= 30 else ""
        inc.append(row)
    inc = pd.DataFrame(inc).sort_values("ipl2026_matches", ascending=False)
    inc["regular"] = inc.ipl2026_matches >= 7
    inc.to_csv(os.path.join(out_dir, "rr_incumbents.csv"), index=False, float_format="%.6g")

    # ---- 2-4. fit table for the top 20 of each group ------------------------------------------------------------------
    out = []
    for label, prof_fn in [("batter", bat_profile), ("bowler", bowl_profile)]:
        rt = rat[label]
        for r in rt[rt["rank"] <= 20].itertuples():
            pr_, g, p = prof_fn(r.player_id)
            row = dict(group=label, rank=r.rank, final_rank=getattr(r, "final_rank", r.rank), player_id=r.player_id, player_name=r.player_name,
                       rating=r.rating, boot_rating_p10=r.boot_rating_p10, boot_rating_p90=r.boot_rating_p90,
                       boot_top10_prob=r.boot_top10_prob, grid_top10_prob=getattr(r, "grid_top10_prob", r.boot_top10_prob),
                       ipl_2026_team=r.ipl_2026_team if isinstance(r.ipl_2026_team, str) else "not in an IPL 2026 squad",
                       national_team=r.national_team if isinstance(r.national_team, str) else "none in data (uncapped)")
            row["overseas_derived"] = row["national_team"] not in ("India", "none in data (uncapped)")
            row.update(pr_)
            row.update(common(p))
            row["availability"] = AVAIL
            row["already_rr"] = row["ipl_2026_team"] == "Rajasthan Royals"
            # gap analysis against RR regulars in the same role
            peers = inc[inc.regular & (inc[f"{label}_role"] == pr_["role"]) & (inc.player_id != r.player_id)]
            rated = peers[peers[f"{label}_eligible"]]
            row["rr_regulars_same_role"] = "; ".join(
                f"{n} ({'#%d, %.2f' % (rk, rg) if el else 'not eligible'})"
                for n, el, rk, rg in zip(peers.player_name, peers[f"{label}_eligible"],
                                         peers[f"{label}_rank"].fillna(0).astype(int), peers[f"{label}_rating"])) or "none"
            if len(rated):
                weakest = rated.sort_values(f"{label}_rating").iloc[0]
                row["weakest_rr_regular"] = weakest.player_name
                row["rating_gap_vs_weakest"] = r.rating - weakest[f"{label}_rating"]
                w_p90 = rat[label].set_index("player_id").boot_rating_p90[weakest.player_id]
                row["weakest_rr_regular_rating_p90"] = w_p90
                supported = r.boot_rating_p10 > w_p90
                row["displacement_call"] = ("already an RR player" if row["already_rr"] else
                                            "would displace (80% intervals do not overlap)" if supported else
                                            "upgrade on point estimate, inside the noise" if row["rating_gap_vs_weakest"] > 0 else
                                            "no upgrade on these numbers")
            else:
                row["weakest_rr_regular"] = ""
                row["rating_gap_vs_weakest"] = np.nan
                row["displacement_call"] = "already an RR player" if row["already_rr"] else "no rated RR regular in this role to compare with"
            disc = "batting" if label == "batter" else "bowling"
            main_phase = max(["powerplay", "middle", "death"], key=lambda ph: pr_[f"share_{ph}"] / {"powerplay": 0.3, "middle": 0.45, "death": 0.25}[ph])
            row["main_phase"] = main_phase
            row["fills_rr_gap_cell"] = (disc, main_phase) in gap_cells
            row["auction_shortlist"] = bool((not row["already_rr"]) and row["fills_rr_gap_cell"] and r.boot_top10_prob >= 0.10)
            out.append(row)
    fit = pd.DataFrame(out)
    fit.to_csv(os.path.join(out_dir, "rr_fit.csv"), index=False, float_format="%.6g")
    print(fit[["group", "rank", "player_name", "role", "main_phase", "ipl_2026_team", "overseas_derived", "weakest_rr_regular",
               "rating_gap_vs_weakest", "displacement_call", "auction_shortlist"]].round(2).to_string())

    # ---- figure ----------------------------------------------------------------------------------------------------------
    plt = setup_matplotlib()
    k = prof[(prof["sample"] == "pressure") & (prof.situation == "all") & (prof.phase != "all")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, disc in zip(axes, ["batting", "bowling"]):
        d = k[k.discipline == disc]
        x = np.arange(3)
        for i, (yr, col) in enumerate([(2025, "#f4a6c0"), (2026, "#e6007e")]):
            v = d[d.year == yr].set_index("phase").reindex(["powerplay", "middle", "death"])
            ax.bar(x + (i - 0.5) * 0.38, v.rr_minus_league, 0.38, color=col, label=f"IPL {yr}")
            for xi, (val, rk) in enumerate(zip(v.rr_minus_league, v.rr_rank_of_teams)):
                ax.text(xi + (i - 0.5) * 0.38, val + (0.8 if val >= 0 else -0.8), f"#{int(rk)}", ha="center",
                        va="bottom" if val >= 0 else "top", fontsize=10)
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x); ax.set_xticklabels(["Powerplay", "Middle", "Death"])
        ax.set_title(f"RR {disc} under pressure")
    axes[0].set_ylabel("NRAE per 100 pressure balls, RR minus league (label = rank of 10)")
    axes[0].legend(frameon=False)
    fig.suptitle("Rajasthan Royals under pressure by phase, IPL 2025 and 2026 (positive = better than league)")
    fig.tight_layout(); fig.savefig(figure_path); plt.close(fig)


if __name__ == "__main__":
    main()
