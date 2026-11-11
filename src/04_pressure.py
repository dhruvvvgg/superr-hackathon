"""Stage 04: leverage index, pressure score, tiers, rule-based variants and validation.

Outputs
  data/interim/pressure.parquet     per delivery: wp_before, wp_after, wpa, leverage, pscore, flags
  outputs/tables/pressure_validation.csv, pressure_composition.csv, pressure_variants.csv
  outputs/figures/leverage_by_over.png, pressure_tier_metrics.png, pressure_composition.png
"""
import json
import os
import pickle

import numpy as np
import pandas as pd

from common import CFG, INTERIM, FIGURES, save_table, setup_matplotlib, checked_merge
from wp_lib import wp_states, TIER_CODE

OUTCOMES = ["dot", "1", "2", "3", "4", "6", "wicket", "wide", "noball"]


def classify(b):
    tr = np.round(b.total_runs.values)
    o = np.select([b.is_wide.values, b.is_noball.values, b.is_wicket.values, tr <= 0, tr == 1, tr == 2,
                   tr == 3, tr <= 5], ["wide", "noball", "wicket", "dot", "1", "2", "3", "4"], default="6")
    return o


def metrics(d):
    faced = d[~d.is_wide]
    legal = d[d.legal]
    out_ = faced.is_wicket & ~faced.dismissal_type.isin(CFG["non_batter_cost_dismissals"])
    return pd.Series(dict(
        deliveries=len(d), balls_faced=len(faced),
        strike_rate=100 * faced.runs.sum() / max(len(faced), 1),
        dot_pct=100 * (faced.runs == 0).mean() if len(faced) else np.nan,
        boundary_pct=100 * (faced.is_four | faced.is_six).mean() if len(faced) else np.nan,
        wicket_pct=100 * out_.mean() if len(faced) else np.nan,
        economy=6 * d.bowler_runs.sum() / max(len(legal), 1),
        mean_leverage=d.leverage.mean(), mean_abs_wpa=d.wpa.abs().mean()))


def main():
    print("Stage 04: pressure")
    b = pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))
    b = b[b.clean].reset_index(drop=True)
    wp = pd.read_parquet(os.path.join(INTERIM, "wp.parquet"))
    b = checked_merge(b, wp[["match_id", "innings", "innings_ball_num", "fold", "wp_before"]],
                      "deliveries+win probability", on=["match_id", "innings", "innings_ball_num"],
                      how="left", validate="1:1")
    assert b.wp_before.notna().all()
    with open(os.path.join(INTERIM, "wp_models.pkl"), "rb") as f:
        pk = pickle.load(f)
    models = pk["models"]
    val = json.load(open(os.path.join(INTERIM, "extras_values.json")))

    # ---- realised win-probability change -----------------------------------------------------
    g = b.groupby(["match_id", "innings"], sort=False)
    nxt = g.wp_before.shift(-1)
    first2 = b[b.innings == 2].groupby("match_id").wp_before.first()
    is_last = nxt.isna()
    end1 = is_last & (b.innings == 1)
    end2 = is_last & (b.innings == 2)
    nxt[end1] = 1.0 - b.match_id[end1].map(first2)
    nxt[end2] = b.bat_win[end2]
    b["wp_after"] = nxt
    assert b.wp_after.notna().all()
    b["wpa"] = b.wp_after - b.wp_before

    # ---- outcome frequencies by phase and innings ----------------------------------------------
    b["outcome"] = classify(b)
    freq = (b.groupby(["innings", "phase"]).outcome.value_counts(normalize=True).unstack(fill_value=0.0)
            .reindex(columns=OUTCOMES, fill_value=0.0))
    save_table(freq.reset_index(), "outcome_frequencies.csv")

    # ---- leverage ----------------------------------------------------------------------------------
    run_o = dict(zip(OUTCOMES, [0, 1, 2, 3, 4, 6, 0, val["wide"], val["Overstep"]]))
    lev = np.zeros(len(b))
    tier_code = b.tier.map(TIER_CODE).values
    P = freq.reindex(pd.MultiIndex.from_arrays([b.innings, b.phase])).values
    for k, mdl in enumerate(models):
        msk = (b.fold == k).values
        d = b[msk]
        for j, o in enumerate(OUTCOMES):
            legal = o not in ("wide", "noball")
            wkt = 1 if o == "wicket" else 0
            r = run_o[o]
            w_new = wp_states(mdl, d.innings.values, d.legal_before.values + (1 if legal else 0),
                              d.score_before.values + r, d.wkts_before.values + wkt, d.target.values,
                              d.runs_last12.values - d.r12_drop.values + r,
                              d.wkts_last12.values - d.w12_drop.values + wkt,
                              np.where(r == 0, d.dot_streak.values + 1, 0), d.venue_avg.values, tier_code[msk])
            dw = w_new - d.wp_before.values
            lev[msk] += P[msk, j] * (np.abs(dw) if CFG["leverage"]["kind"] == "mean_abs" else dw * dw)
    if CFG["leverage"]["kind"] != "mean_abs":
        lev = np.sqrt(lev)                      # root-mean-square swing
    b["leverage_raw"] = lev
    b["leverage"] = lev / lev.mean()
    print(f"  mean raw leverage (expected |dWP| per ball): {lev.mean():.4f}")
    from scipy.stats import spearmanr as _sp
    lev_valid = pd.DataFrame([dict(
        leverage_kind=CFG["leverage"]["kind"],
        spearman_leverage_vs_realised_abs_wpa=_sp(lev, b.wpa.abs()).statistic,
        pearson_leverage_vs_realised_abs_wpa=np.corrcoef(lev, b.wpa.abs())[0, 1],
        mean_abs_wpa_top20pct=b.wpa.abs()[lev >= np.quantile(lev, 0.8)].mean(),
        mean_abs_wpa_bottom50pct=b.wpa.abs()[lev < np.quantile(lev, 0.5)].mean())])
    save_table(lev_valid, "leverage_validity.csv")

    b["pscore"] = b.groupby("innings").leverage.rank(pct=True) * 100
    b["pscore_global"] = b.leverage.rank(pct=True) * 100
    pc = CFG["pressure"]
    b["ptier"] = np.select([b.pscore >= pc["extreme"], b.pscore >= pc["high"], b.pscore >= pc["normal"]],
                           ["Extreme", "High", "Normal"], default="Low")
    b["pA"] = b.pscore >= pc["high"]
    b["pB"] = b.wp_before.between(0.25, 0.75) & ((b.balls_left <= 48) | (b.wkts_before >= 5))
    b["pC"] = b.pscore >= 90
    b["pD"] = b.pscore >= 70
    b["pE"] = (b.over >= 16) & b.wp_before.between(0.2, 0.8)
    b["pF"] = b.pscore_global >= pc["high"]

    # ---- validation: tiers, overall and with phase, innings and wickets held fixed ---------------
    order = ["Low", "Normal", "High", "Extreme"]
    b["wk_band"] = pd.cut(b.wkts_before, [-1, 2, 5, 10], labels=["0-2", "3-5", "6+"]).astype(str)
    rows = []
    overall = b.groupby("ptier").apply(metrics, include_groups=False).reindex(order)
    for t, r in overall.iterrows():
        rows.append(dict(table="tier overall", innings="all", phase="all", wk_band="all", tier=t, **r.to_dict()))
    b["pgroup"] = np.where(b.pA, "Pressure (High+Extreme)", np.where(b.ptier == "Normal", "Normal", "Low"))
    cell = b.groupby(["innings", "phase", "wk_band", "pgroup"]).apply(metrics, include_groups=False).reset_index()
    for r in cell.itertuples(index=False):
        rows.append(dict(table="within cell", innings=r.innings, phase=r.phase, wk_band=r.wk_band, tier=r.pgroup,
                         **{k: getattr(r, k) for k in overall.columns}))
    # standardised shift Normal -> Pressure: weighted mean of within-cell differences
    mets = ["strike_rate", "dot_pct", "boundary_pct", "wicket_pct", "economy"]
    piv = cell.pivot_table(index=["innings", "phase", "wk_band"], columns="pgroup", values=mets + ["balls_faced"])
    wgt = np.minimum(piv[("balls_faced", "Normal")], piv[("balls_faced", "Pressure (High+Extreme)")]).fillna(0)
    ok = wgt >= 200
    raw_n = b[b.pgroup == "Normal"].pipe(metrics)
    raw_p = b[b.pA].pipe(metrics)
    for mname in mets:
        diff = (piv[(mname, "Pressure (High+Extreme)")] - piv[(mname, "Normal")])[ok]
        rows.append(dict(table="shift Normal->Pressure", innings="all", phase="all", wk_band="all", tier=mname,
                         raw_shift=raw_p[mname] - raw_n[mname],
                         within_cell_shift=np.average(diff, weights=wgt[ok]),
                         cells_used=int(ok.sum()), cells_same_sign=int((np.sign(diff) == np.sign(np.average(diff, weights=wgt[ok]))).sum())))
    save_table(pd.DataFrame(rows), "pressure_validation.csv")
    print(overall[["deliveries", "strike_rate", "dot_pct", "boundary_pct", "wicket_pct", "economy", "mean_abs_wpa"]].round(2).to_string())
    print(pd.DataFrame(rows).query("table == 'shift Normal->Pressure'")[["tier", "raw_shift", "within_cell_shift", "cells_used", "cells_same_sign"]].round(3).to_string())

    # ---- composition of the pressure sample ----------------------------------------------------
    b["rrr_band"] = np.where(b.innings == 1, "first innings",
                             pd.cut(b.rrr, [-np.inf, 6, 8, 10, 12, 15, np.inf],
                                    labels=["<6", "6-8", "8-10", "10-12", "12-15", "15+"]).astype(str))
    comp_rows = []
    for dim in ["innings", "phase", "wk_band", "rrr_band", "tier"]:
        a = b[b.pA][dim].value_counts(normalize=True)
        al = b[dim].value_counts(normalize=True)
        for k in al.index:
            comp_rows.append(dict(dimension=dim, level=str(k), share_of_pressure=a.get(k, 0.0), share_of_all=al[k],
                                  pressure_rate_within_level=b[b[dim] == k].pA.mean()))
    comp_rows.append(dict(dimension="win probability", level="pressure balls with WP in 0.2-0.8",
                          share_of_pressure=b[b.pA].wp_before.between(0.2, 0.8).mean(),
                          share_of_all=b.wp_before.between(0.2, 0.8).mean(), pressure_rate_within_level=np.nan))
    comp_rows.append(dict(dimension="win probability", level="pressure balls with WP below 0.05 or above 0.95",
                          share_of_pressure=((b[b.pA].wp_before < 0.05) | (b[b.pA].wp_before > 0.95)).mean(),
                          share_of_all=((b.wp_before < 0.05) | (b.wp_before > 0.95)).mean(), pressure_rate_within_level=np.nan))
    save_table(pd.DataFrame(comp_rows), "pressure_composition.csv")

    # ---- variants ----------------------------------------------------------------------------------
    vr = []
    for v in "ABCDEF":
        f = b[f"p{v}"]
        inter = (f & b.pA).sum()
        vr.append(dict(variant=v, share_of_deliveries=f.mean(), phi_with_A=np.corrcoef(f, b.pA)[0, 1],
                       jaccard_with_A=inter / (f | b.pA).sum(), share_of_variant_inside_A=inter / max(f.sum(), 1),
                       share_innings1=(b[f].innings == 1).mean(), mean_leverage=b[f].leverage.mean()))
    vdesc = {"A": "primary: leverage percentile >= 80 within innings number",
             "B": "WP in 0.25-0.75 and (balls left <= 48 or wickets lost >= 5)",
             "C": "leverage percentile >= 90", "D": "leverage percentile >= 70",
             "E": "overs 16-20 and WP in 0.2-0.8", "F": "leverage percentile >= 80, global (both innings pooled)"}
    vt = pd.DataFrame(vr)
    vt["definition"] = vt.variant.map(vdesc)
    save_table(vt, "pressure_variants.csv")
    print(vt.round(3).to_string())

    # ---- figures -----------------------------------------------------------------------------------
    plt = setup_matplotlib()
    fig, ax = plt.subplots(figsize=(9, 5))
    for inn, col in [(1, "#1f6fb2"), (2, "#d1495b")]:
        d = b[b.innings == inn].groupby("over").leverage.agg(["mean", lambda s: s.quantile(0.9)])
        ax.plot(d.index, d["mean"], marker="o", color=col, label=f"Innings {inn}: mean")
        ax.plot(d.index, d.iloc[:, 1], ls="--", color=col, alpha=0.7, label=f"Innings {inn}: 90th percentile")
    ax.axhline(1, color="grey", lw=1)
    ax.set_xlabel("Over"); ax.set_ylabel("Leverage index (1 = average ball)")
    ax.set_xticks(range(1, 21)); ax.set_title("Leverage by over"); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(FIGURES, "leverage_by_over.png")); plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5))
    cols = ["#9ecae1", "#6baed6", "#f29e4c", "#d1495b"]
    for ax, (mname, lab) in zip(axes, [("strike_rate", "Strike rate"), ("dot_pct", "Dot ball %"),
                                        ("wicket_pct", "Wickets per 100 balls"), ("economy", "Economy (runs per over)")]):
        ax.bar(order, overall[mname].values, color=cols)
        for i, v_ in enumerate(overall[mname].values):
            ax.text(i, v_, f"{v_:.1f}", ha="center", va="bottom")
        ax.set_title(lab); ax.set_xlabel("Pressure tier")
    fig.suptitle("Batting and bowling outcomes by pressure tier (all clean matches)")
    fig.tight_layout(); fig.savefig(os.path.join(FIGURES, "pressure_tier_metrics.png")); plt.close(fig)

    ct = pd.DataFrame(comp_rows)
    dims = [("innings", "Innings"), ("phase", "Phase"), ("wk_band", "Wickets lost"), ("rrr_band", "Required rate band")]
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))
    for ax, (dim, lab) in zip(axes, dims):
        d = ct[ct.dimension == dim].copy()
        if dim == "phase":
            d = d.set_index("level").reindex(["powerplay", "middle", "death"]).reset_index()
        elif dim == "rrr_band":
            d = d.set_index("level").reindex(["first innings", "<6", "6-8", "8-10", "10-12", "12-15", "15+"]).reset_index()
        else:
            d = d.sort_values("level")
        x = np.arange(len(d))
        ax.bar(x - 0.2, 100 * d.share_of_all, 0.4, color="#9ecae1", label="All deliveries")
        ax.bar(x + 0.2, 100 * d.share_of_pressure, 0.4, color="#d1495b", label="Pressure sample")
        ax.set_xticks(x); ax.set_xticklabels(d.level, rotation=30 if dim == "rrr_band" else 0)
        ax.set_title(lab); ax.set_ylabel("Share of deliveries (%)")
    axes[0].legend(frameon=False)
    fig.suptitle("Composition of the pressure sample (pressure score >= 80)")
    fig.tight_layout(); fig.savefig(os.path.join(FIGURES, "pressure_composition.png")); plt.close(fig)

    keep = ["match_id", "innings", "innings_ball_num", "fold", "wp_before", "wp_after", "wpa", "leverage",
            "pscore", "pscore_global", "ptier", "pA", "pB", "pC", "pD", "pE", "pF"]
    b[keep].to_parquet(os.path.join(INTERIM, "pressure.parquet"), index=False)
    print(f"  wrote pressure.parquet ({len(b)} rows)")


if __name__ == "__main__":
    main()
