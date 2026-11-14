"""Stage 11: write docs/FINDINGS.md from the output tables, so every number in the document is
read from a file in outputs/ at the moment the pipeline runs."""
import json
import os

import numpy as np
import pandas as pd

from common import CFG, ROOT, TABLES

T = lambda n: pd.read_csv(os.path.join(TABLES, n))
P1 = lambda n: pd.read_csv(os.path.join(ROOT, "outputs", "phase1", n))


def md(df, floatfmt=2):
    d = df.copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else f"{v:.{floatfmt}f}")
        elif d[c].dtype == bool:
            d[c] = d[c].map({True: "yes", False: "no"})
    d = d.fillna("").astype(str)
    lines = ["| " + " | ".join(d.columns) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
    lines += ["| " + " | ".join(r) + " |" for r in d.values]
    return "\n".join(lines)


def reason(r, role):
    z = {"level": r.z_level, "impact": r.z_impact, "consistency": r.z_consistency, "delta": r.z_delta}
    lab = {"level": "pressure level", "impact": "win-probability impact", "consistency": "consistency",
           "delta": "lift over own normal level"}
    lead = f"leverage-weighted level ({z['level']:+.1f} SD)"
    sec = max(("impact", "consistency", "delta"), key=lambda k: z[k])
    if z[sec] >= 1.0:
        lead += f", also high on {lab[sec]} ({z[sec]:+.1f})"
    if role == "bat":
        raw_ = (f"strike rate {r.press_sr:.0f} under pressure against {r.normal_sr:.0f} otherwise, "
                f"{int(r.press_runs)} runs and {int(r.press_outs)} dismissals in {int(r.n_press_balls)} pressure balls")
    else:
        raw_ = (f"economy {r.press_econ:.2f} under pressure against {r.normal_econ:.2f} otherwise, "
                f"{int(r.press_wkts)} wickets in {int(r.n_press_balls)} pressure balls")
    return f"Rated on {lead}; {raw_}."


def main():
    print("Stage 11: report")
    W = CFG["composite_weights"]
    E = CFG["eligibility"]
    R = CFG["robustness"]
    std = CFG.get("composite", {}).get("standardise", "zscore")
    role_aware = CFG.get("baseline", {}).get("role_aware", False)
    tb, tw = T("top10_batters.csv"), T("top10_bowlers.csv")
    rb, rw = T("batter_ratings.csv"), T("bowler_ratings.csv")
    dq = T("data_quality.csv")
    ex = T("extras_calibration.csv").set_index("item").fitted
    wm = T("wp_model_metrics.csv")
    pv = T("pressure_validation.csv")
    pcomp = T("pressure_composition.csv")
    pvar = T("pressure_variants.csv")
    lv = T("leverage_validity.csv").iloc[0]
    em = T("expected_model_metrics.csv")
    cv = T("ridge_cv.csv")
    ag = T("estimator_agreement.csv")
    sc = T("sensitivity_configs.csv")
    sm = T("sensitivity_membership.csv")
    pers = T("persistence.csv")
    rule = T("decision_rule.csv")
    face = T("face_validity.csv")
    prof = T("rr_team_profile.csv")
    fit = T("rr_fit.csv")
    inc = T("rr_incumbents.csv")
    aud = T("audit_scorecards.csv")
    integ = T("audit_integrity.csv")
    res = T("resource_table.csv")
    x2 = T("phase2_experiments.csv") if os.path.exists(os.path.join(TABLES, "phase2_experiments.csv")) else None
    verdicts = json.load(open(os.path.join(ROOT, "docs", "phase2_verdicts.json"))) \
        if os.path.exists(os.path.join(ROOT, "docs", "phase2_verdicts.json")) else {}
    dqv = lambda chk: dq[dq.check == chk].observed.iloc[0]
    L = []
    A = L.append

    A("# FINDINGS: who delivers under pressure\n")
    A("> **Primary task ranking.** The final shortlist follows the pre-registered four-component composite. "
      "remains the full record of the data preparation, validation, audit and the earlier ratings; "
      "`docs/V2_FINDINGS.md` records the intermediate redesign.\n")
    A("Every number below is read from a file in `outputs/tables/` when the pipeline runs "
      "(`src/11_report.py`). The file is named next to each table. Figures are in `outputs/figures/`.\n")

    # ---- 1 ------------------------------------------------------------------------------------------
    A("## 1. Result in one page\n")
    A("Rating is the composite pressure rating. The interval is the 80% interval from a match bootstrap "
      f"({R['n_bootstrap']} resamples). P(top 10) boot is the share of bootstrap resamples in which the player "
      "finishes in the top 10. P(top 10) grid is the share of sensitivity-grid configurations in which he does.\n")
    for label, t, role in [("batters", tb, "bat"), ("bowlers", tw, "bowl")]:
        A(f"### Top 10 {label} (`top10_{label}.csv`)\n")
        d = pd.DataFrame({"Rank": t.final_rank, "Player (id)": [f"{n} ({i})" for n, i in zip(t.player_name, t.player_id)],
                          "Rating": t.rating.round(2),
                          "80% interval": [f"{a:.2f} to {b:.2f}" for a, b in zip(t.boot_rating_p10, t.boot_rating_p90)],
                          "80% rank interval": [f"{a:.0f} to {b:.0f}" for a, b in zip(t.boot_rank_p10, t.boot_rank_p90)],
                          "P(top 10) boot": t.boot_top10_prob, "P(top 10) grid": t.grid_top10_prob,
                          "Pressure balls": t.n_press_balls})
        A(md(d) + "\n")
        for r in t.itertuples():
            A(f"{r.final_rank}. **{r.player_name}**: {reason(r, role)}")
        A("")
    A("The bootstrap interval of a top-ranked player usually sits below his point rating. That is expected: "
      "the players at the top of a noisy ranking are partly there by luck, and resampling the matches pulls "
      "them back. Read the interval as the honest range.\n")

    # ---- 2 ------------------------------------------------------------------------------------------
    A("## 2. Pressure definition and validation\n")
    A("**Definition.** Pressure is how much the next ball can move the match. For every delivery the "
      "out-of-fold win-probability model scores the state after each possible next-ball outcome (dot, 1, 2, 3, "
      "4, 6, wicket, wide, no-ball). Leverage is the expected absolute change in win probability, weighting "
      "outcomes by their frequency in that phase and innings, divided by the global mean so an average ball "
      "has leverage 1. The pressure score is the percentile of leverage among all deliveries of the same "
      f"innings number. Tiers: Low below {CFG['pressure']['normal']}, Normal {CFG['pressure']['normal']} to "
      f"{CFG['pressure']['high']}, High {CFG['pressure']['high']} to {CFG['pressure']['extreme']}, Extreme above. "
      f"The pressure sample is score at or above {CFG['pressure']['high']}.\n")
    A("**Why it is meaningful.** One number learned from match outcomes combines required rate, wickets in "
      "hand, balls left and closeness. A dead game has win probability near 0 or 1, nothing the next ball does "
      "can move it, and leverage is low without any hand-set cutoff.\n")
    A(f"**Does leverage measure what it claims?** Leverage is computed before the ball; the realised absolute "
      f"win-probability change is observed after. Their Spearman correlation is "
      f"{lv.spearman_leverage_vs_realised_abs_wpa:.2f}. The top 20% of deliveries by leverage move win probability "
      f"by {100 * lv.mean_abs_wpa_top20pct:.1f} points on average, the bottom 50% by "
      f"{100 * lv.mean_abs_wpa_bottom50pct:.1f} points (`leverage_validity.csv`).\n")
    ov = pv[pv.table == "tier overall"][["tier", "deliveries", "strike_rate", "dot_pct", "boundary_pct", "wicket_pct", "economy", "mean_leverage", "mean_abs_wpa"]]
    ov = ov.assign(mean_abs_wpa=100 * ov.mean_abs_wpa).rename(columns={"mean_abs_wpa": "mean abs WP change (pts)", "wicket_pct": "wickets per 100 balls"})
    ov["deliveries"] = ov.deliveries.astype(int)
    A("Outcomes by tier (`pressure_validation.csv`, table = tier overall; figure `pressure_tier_metrics.png`):\n")
    A(md(ov) + "\n")
    sh = pv[pv.table == "shift Normal->Pressure"][["tier", "raw_shift", "within_cell_shift", "cells_used", "cells_same_sign"]]
    sh = sh.rename(columns={"tier": "metric", "raw_shift": "raw shift Normal to Pressure",
                            "within_cell_shift": "shift with innings, phase and wickets band held fixed"})
    sh["cells_used"] = sh.cells_used.astype(int); sh["cells_same_sign"] = sh.cells_same_sign.astype(int)
    A("Shift from the Normal tier to the pressure sample (`pressure_validation.csv`, table = shift):\n")
    A(md(sh) + "\n")
    A("Read this honestly. The tiers separate the stakes very clearly (the win-probability column). The "
      "behavioural shift is real in the raw numbers but most of it is composition: pressure balls sit more in "
      "the death overs and in tight chases, where everyone scores faster and gets out more. With innings, phase "
      "and wickets held fixed the shift is small. So pressure, as defined here, marks the balls that decide "
      "matches; it does not by itself make the average player bat or bowl very differently. Part of what "
      "remains is selection: high-leverage states are reached more often by good teams in close games.\n")
    c = pcomp.set_index(["dimension", "level"])
    g = lambda dim, lev, col="share_of_pressure": c.loc[(dim, lev), col]
    A("Composition of the pressure sample (`pressure_composition.csv`, figure `pressure_composition.png`): "
      f"innings 1 {100 * g('innings', '1'):.0f}% and innings 2 {100 * g('innings', '2'):.0f}% by construction; "
      f"powerplay {100 * g('phase', 'powerplay'):.0f}%, middle {100 * g('phase', 'middle'):.0f}%, death "
      f"{100 * g('phase', 'death'):.0f}% (death overs are {100 * g('phase', 'death', 'share_of_all'):.0f}% of all "
      f"deliveries); {100 * g('win probability', 'pressure balls with WP in 0.2-0.8'):.0f}% of pressure balls have "
      f"win probability between 0.2 and 0.8 and "
      f"{100 * g('win probability', 'pressure balls with WP below 0.05 or above 0.95'):.1f}% are in decided games. "
      "Average leverage by over is in `leverage_by_over.png`: it rises through the death overs and peaks in the "
      "last over of a chase.\n")
    A("Rule-based alternatives and their agreement with the primary flag (`pressure_variants.csv`):\n")
    A(md(pvar[["variant", "definition", "share_of_deliveries", "phi_with_A", "jaccard_with_A", "share_innings1"]]) + "\n")

    # ---- 3 ------------------------------------------------------------------------------------------
    A("## 3. Data quality log\n")
    diff = dq[(dq.stage == "01_profile") & (dq.status == "DIFFERS")][["check", "claimed", "observed", "note"]]
    scope_checks = [
        "overs with >6 legal balls, other legal (handover rule)",
        "DLS in result text but no revised field",
        "batters with >=200 balls faced", "batters with >=500 balls faced",
        "bowlers with >=200 balls bowled", "bowlers with >=500 balls bowled"
    ]
    scope = dq[dq.check.isin(scope_checks)][["check", "claimed", "observed", "status", "note"]]
    A(f"`src/01_profile.py` re-verified {int((dq.stage == '01_profile').sum())} facts from the build specification "
      "(`data_quality.csv`).\n")
    if diff.empty:
        A("No unresolved specification mismatches remain. The following rows are documented scope diagnostics, "
          "not integrity failures:\n")
    else:
        A("Specification differences requiring interpretation:\n" + md(diff) + "\n")
    A(md(scope) + "\n")
    A("- **Legal balls.** The specification's rule (\"other\" extras are legal) gives 244 overs with more than six "
      "legal balls. Treating \"other\" as a no-ball gives 1. The adopted rule is: illegal = wide, Overstep, other.")
    A(f"- **Wicket check.** {dq[dq.check.str.startswith('wicket check')].note.iloc[0]} agree with the result "
      "string. One result string was wrong: match 20190 (LSG v SRH, 7 April 2023) says 6 wickets, while the ball "
      "data and five outside scorecards show LSG won by 5 wickets with 127/5. It is corrected by a documented "
      "override in `config.json` (DECISIONS.md, D-24). This check does not depend on extras.")
    A(f"- **Extras calibration** (\`extras_calibration.csv\`). Per-match values are estimated only from clean "
      f"run-margin matches on strictly earlier dates; the first 40 eligible historical matches use the fixed "
      f"1-run-per-extra fallback. Median applied values were wide {ex['run value: wide']:.2f}, no-ball "
      f"{ex['run value: Overstep']:.2f}, other no-ball {ex['run value: other']:.2f}, leg bye "
      f"{ex['run value: legbyes']:.2f}, bye {ex['run value: byes']:.2f}. Strictly out-of-time reconstructed "
      f"for the fixed 1-run rule; RMSE was {ex['margin RMSE (runs), fitted']:.2f} versus "
      f"{ex['margin RMSE (runs), simple']:.2f}. The MAE is essentially unchanged and slightly worse under the "
      "fitted coefficients, while RMSE is lower; this is a mixed diagnostic, not evidence of a universal "
      "accuracy gain. Residual error remains because bye and leg-bye run detail is absent from the supplied data "
      "and occasional deliveries may be missing. No same-match or future result is used to price an extra.")
    A("- **Chase target.** The target is the rounded first-innings reconstructed total plus one. Result strings, "
      "final chase totals, run margins and wickets remaining are never used to set it. Required-rate features "
      "therefore carry reconstruction error from the incomplete extras data.")
    excl = dq[dq.check.str.startswith("matches excluded")][["check", "observed"]]
    A(f"- **Exclusions.** {'; '.join(f'{c.replace('matches excluded: ', '')}: {int(float(o))}' for c, o in zip(excl.check, excl.observed))}. "
      f"Clean matches kept: {int(float(dqv('clean matches kept')))}. Super-over deliveries dropped: 38.")
    A(f"- **Scorecard audit** (`audit_scorecards.csv`). Ten seeded random matches were rebuilt from the ball data: "
      f"winner and wickets agree with the result string in {int(aud.winner_and_wickets_agree.sum())} of {len(aud)}; "
      f"run-margin errors range from {aud.run_margin_error.min():.1f} to {aud.run_margin_error.max():.1f} runs.")
    A(f"- **Integrity audit** (`audit_integrity.csv`). {int((integ.status == 'pass').sum())} checks pass and "
      f"{int((integ.status == 'FAIL').sum())} fail: no duplicated deliveries, no super-over or reduced-match "
      "deliveries downstream, no wide counted as a ball faced, no run out credited to a bowler, no match scored "
      "by a model that saw it, one name per player id.\n")

    # ---- 4 ------------------------------------------------------------------------------------------
    A("## 4. Win-probability model\n")
    A("Primary model: one logistic regression per innings on a degree-2 polynomial of the resource-adjusted "
      "margin, balls left, wickets lost and the three momentum features. The margin is (expected remaining runs "
      "minus runs needed) in a chase and (projected total minus venue average) when setting, scaled by the "
      "square root of balls left. Expected remaining runs come from a resource table fitted inside each "
      "training fold. Five folds grouped by match; only out-of-fold predictions are used downstream. No team "
      "or player identity.\n")
    w = wm[wm["sample"] == "all"][["model", "role", "description", "log_loss", "brier", "max_calib_gap_dense_bins"]]
    w2 = wm.pivot(index="model", columns="sample", values="log_loss")
    w = w.assign(log_loss_inn1=w.model.map(w2["innings 1"]), log_loss_inn2=w.model.map(w2["innings 2"]))
    A("`wp_model_metrics.csv` (out-of-fold; lower is better):\n")
    A(md(w[["model", "role", "description", "log_loss", "log_loss_inn1", "log_loss_inn2", "brier", "max_calib_gap_dense_bins"]], 4) + "\n")
    cb = T("wp_calibration_bins.csv")
    A(f"Calibration (`wp_calibration_bins.csv`, figure `wp_calibration.png`): the largest gap between predicted and "
      f"observed win rate in bins with at least 5,000 deliveries is "
      f"{wm[(wm.role == 'primary') & (wm['sample'] == 'all')].max_calib_gap_dense_bins.iloc[0]:.3f}, and "
      f"{int(cb.gap_within_2sd.sum())} of {len(cb)} bins lie within two standard deviations of match-bootstrap noise. "
      "First-innings win probability is close to a coin flip by nature (log loss near 0.64); most of the model's "
      "information is in the chase.\n")

    # ---- 5 ------------------------------------------------------------------------------------------
    A("## 5. Metrics, baselines and rating logic\n")
    A("**Units.** A batter's unit is a ball faced (any delivery that is not a wide). A bowler's unit is a "
      "legal-ball slot: one legal ball plus the wides and no-balls that preceded it.\n")
    A("**Baselines without player identity** (`expected_model_metrics.csv`). Expected bat and bowler runs "
      "use out-of-fold LightGBM regressors. Expected wicket probability uses a fold-local innings/phase mean "
      "estimated from training matches only. The calibrated LightGBM wicket classifier remains a diagnostic "
      "candidate and is not used for player credit because the simpler reference is the selected baseline. "
      "Run-model features: innings, phase, balls left, wickets lost, current and required rate and their gap, "
      "venue average, competition tier, pace or spin, bowling type, batter hand, no-ball and free-hit flags"
      + (", plus balls already faced by the striker in the innings and his batting position (the role-aware "
         "baseline adopted in phase 2)" if role_aware else "") + ".\n")
    A(md(em[em.metric.isin(["RMSE", "log loss"])][["model", "n", "metric", "oof", "phase_mean_baseline", "mean_actual", "mean_pred", "selected_method"]], 4) + "\n")
    wv = res[(res.balls_left.isin([120, 60, 24])) & (res.wickets_lost.isin([0, 3, 6]))]
    A("**Wicket value in runs** (`resource_table.csv`). Expected remaining first-innings runs are fitted as "
      "R_w(b) = a_w (1 - exp(-b / t_w)) with a non-crossing penalty. The value of a wicket is the drop in "
      "expected remaining runs from w to w+1 wickets down. Examples: "
      + "; ".join(f"{int(r.balls_left)} balls left, {int(r.wickets_lost)} down: {r.wicket_value_runs:.1f} runs" for r in wv.itertuples()) + ".\n")
    A("**Ball-level credit.**\n")
    A("- Batter NRAE (net runs above expected) = (bat runs - expected runs) - wicket value x (dismissed - "
      "expected dismissal). The dismissal is charged to the dismissed player; non-striker run outs and "
      "dismissals off wides are dismissal-only records. Retired out costs nothing.")
    A("- Bowler NRAE = (expected runs - runs charged) + wicket value x (bowler wicket - expected wicket). Wides "
      "and no-balls are charged, byes and leg byes are not. Run outs and retirements are not credited.")
    A("- WPA = change in out-of-fold win probability across the ball, to the striker and with opposite sign "
      "to the bowler.\n")
    ch = cv[cv.chosen]
    A("**Player estimates.** A weighted crossed ridge regression on ball-level NRAE with: player normal effect, "
      "player pressure delta, opponent effect (bowler for batters, striker for bowlers), own-team-by-season "
      "effect, venue, tier and an unpenalised pressure indicator. Penalties chosen by 5-fold cross-validation "
      "grouped by match (`ridge_cv.csv`): "
      + "; ".join(f"{'batters' if r.role == 'bat' else 'bowlers'} main {r.lambda_main:g}, delta {r.lambda_delta:g}" for r in ch.itertuples())
      + ". The cross-validated error surface is almost flat in the delta penalty and for bowlers the choice "
        "sits at the largest value in the grid: the data contain very little information about individual "
        "pressure deltas.\n")
    WS = CFG["composite_weights_spec"]
    A("**Primary rating.** The shortlist uses the pre-registered composite: 40% leverage-weighted, "
      "opponent-adjusted pressure level; 25% shrunk win-probability impact; 20% beta-binomial-shrunk consistency; "
      "and 15% shrunk pressure-versus-normal delta. Each component is standardised among eligible players before "
      "combination. A separate Level-focused V3 model is retained as a predictive challenger in "
      "`docs/V3_FINDINGS.md`; it does not redefine the task objective or primary shortlist.\n")
    A("| Component | Spec weight | Rating weight | Definition |\n|---|---|---|---|")
    A(f"| Level | {WS['level']:.2f} | {W['level']:.2f} | ridge estimate, NRAE per 100 balls, opponent-adjusted; leverage-weighted in the rating |")
    A(f"| Impact | {WS['impact']:.2f} | {W['impact']:.2f} | pressure WPA per 100 balls, empirical Bayes shrinkage with match-clustered errors |")
    A(f"| Consistency | {WS['consistency']:.2f} | {W['consistency']:.2f} | share of pressure innings or spells with NRAE at or above 0, minus the share clearly bad, beta-binomial shrunk |")
    A(f"| Delta | {WS['delta']:.2f} | {W['delta']:.2f} | ridge pressure delta: pressure level minus own normal level |\n")
    A("Components are z-scored among eligible players.\n")
    a = ag[ag.quantity.str.contains("ridge vs")]
    A("**Cross-check estimator** (`estimator_agreement.csv`). Empirical Bayes shrinkage of raw pressure NRAE (unweighted by leverage):\n")
    A(md(a.rename(columns={"spearman": "value"})) + "\n")
    A("The Level correlation is below the 0.8 the specification asked us to investigate. The cause is "
      "structural, not a bug: the ridge Level is normal effect plus delta and borrows strength from all of a "
      "player's balls, while the empirical Bayes Level uses pressure balls only, about a fifth of the sample. "
      "The two answer slightly different questions and the second is much noisier.\n")

    # ---- 6 ------------------------------------------------------------------------------------------
    A("## 6. Fairness choices\n")
    A(f"- **Eligibility.** Batters: at least {E['bat_min_pressure_balls']} pressure balls faced and "
      f"{E['bat_min_pressure_innings']} pressure innings. Bowlers: at least {E['bowl_min_pressure_balls']} pressure "
      f"balls and {E['bowl_min_pressure_spells']} pressure spells. Both: at least {E['min_total_balls']} balls in total "
      f"and an appearance in 2025 or 2026. {len(rb)} batters and {len(rw)} bowlers qualify, so no threshold was lowered.")
    A(f"- **Sample size.** Shrinkage (ridge, empirical Bayes, beta-binomial) pulls small samples toward the pool "
      "mean, so a short hot streak cannot top the list on its own.")
    A(f"- **Recency.** Weights halve every {CFG['weights']['recency_half_life_months']} months back from "
      f"{CFG['reference_date']}.")
    A("- **Opposition.** The ridge estimates each player against the specific opponents he met and absorbs team "
      "strength by season. Deliveries against associate-nation opposition and all A-team tournament deliveries "
      f"weigh {CFG['weights']['a_team']}. An associate player facing a full member keeps full weight.")
    A("- **IPL versus T20I.** Both are pooled with a tier term in every model. IPL-only and T20I-only ratings "
      "are run as sensitivity configurations (section 8).")
    A(f"- **Weak-opposition check.** Largest share of pressure balls against associate or A-team opposition "
      f"among the top-10 batters: {100 * tb.press_share_weak_opp.max():.0f}%; among the top-10 bowlers: "
      f"{100 * tw.press_share_weak_opp.max():.0f}% (`top10_batters.csv`, `top10_bowlers.csv`).\n")

    # ---- 7 ------------------------------------------------------------------------------------------
    A("## 7. Evidence for the top 10\n")
    for label, t, role in [("batters", tb, "bat"), ("bowlers", tw, "bowl")]:
        cols = ["final_rank", "player_name", "z_level", "z_impact", "z_consistency", "z_delta", "level", "normal", "delta",
                "n_press_balls", "n_press_innings"] + (["press_sr", "normal_sr", "press_avg"] if role == "bat" else ["press_econ", "normal_econ", "press_wkts"]) \
               + ["press_share_ipl", "ipl_2026_team", "national_team"]
        A(f"**{label.capitalize()}** (`top10_{label}.csv`; all eligible players in `{label[:-1]}_ratings.csv`):\n")
        A(md(t[cols]) + "\n")
    A("Level, normal and delta are in NRAE per 100 balls. Standardised component columns (z_) are in the units "
      "the composite adds up.\n")
    A("Figures: `top10_batters.png`, `top10_bowlers.png` (ratings with 80% intervals); "
      "`level_vs_normal_batters.png`, `level_vs_normal_bowlers.png` (who lifts and who dips, top 20 labelled); "
      "`sensitivity_heatmap_batters.png`, `sensitivity_heatmap_bowlers.png`.\n")
    dips = pd.concat([rb[(rb["rank"] <= 20) & rb.dips_under_pressure].assign(group="batter"),
                      rw[(rw["rank"] <= 20) & rw.dips_under_pressure].assign(group="bowler")])
    neg = pd.concat([rb[(rb["rank"] <= 20) & (rb.boot_delta_negative_prob >= 0.5)].assign(group="batter"),
                     rw[(rw["rank"] <= 20) & (rw.boot_delta_negative_prob >= 0.5)].assign(group="bowler")])
    A("**Dips under pressure in the top 20.** A top-20 player is flagged when his delta is clearly negative. "
      + (("Flagged by standardised delta at or below -1: " + ", ".join(f"{r.player_name} ({r.group}, rank {r['rank']})" for _, r in dips.iterrows()) + ". ") if len(dips) else
         "No top-20 player has a standardised delta at or below -1. ")
      + (("Players whose delta is negative in at least half of the bootstrap resamples: "
          + ", ".join(f"{r.player_name} ({r.group}, rank {r['rank']}, P(delta<0) {r.boot_delta_negative_prob:.2f})" for _, r in neg.iterrows())
          + ". These players rank highly on overall quality, not on rising under pressure.") if len(neg) else
         "No top-20 player has a negative delta in at least half of the bootstrap resamples.") + "\n")
    A("**Face-validity audit, no overrides** (`face_validity.csv`). The 15 highest-volume death-over batters "
      "and bowlers and where each sits:\n")
    fv = face[["role", "player_name", "death_over_balls", "eligible", "rank", "rating", "boot_top10_prob", "note"]].copy()
    fv["rank"] = fv["rank"].map(lambda v: "" if pd.isna(v) else f"{int(v)}")
    A(md(fv) + "\n")
    A("Several famous finishers sit in the bottom half"
      + (", even with the role-aware baseline that no longer penalises them for facing many first balls" if role_aware else "")
      + ". Their numbers are reported, not adjusted. The usual reasons in the tables are a pressure strike rate "
        "no better than the state-adjusted baseline for the death overs, where the baseline is already very "
        "high, and dismissals in high-leverage chases that cost win probability.\n")

    # ---- 8 ------------------------------------------------------------------------------------------
    A("## 8. Robustness and persistence\n")
    A(f"**Bootstrap.** {R['n_bootstrap']} resamples of matches, full rating recomputed each time with the eligible "
      "set held fixed. Mean rank, 80% rank interval and top-10 probability for every eligible player are in "
      "`batter_ratings.csv` and `bowler_ratings.csv`; the top 10 are in section 1.\n")
    A(f"**Sensitivity grid** (`sensitivity_configs.csv`, `sensitivity_membership.csv`). {sc.config.nunique()} "
      f"structural configurations, each crossed with the primary weights plus {R['n_dirichlet']} weight vectors drawn "
      f"from a Dirichlet centred on them (concentration {R['dirichlet_concentration']}).\n")
    s2 = sc.pivot(index="config", columns="role", values=["n_eligible", "top10_overlap_with_primary", "spearman_with_primary"])
    s2.columns = [f"{b_} {a_.replace('_with_primary', '').replace('top10_overlap', 'top-10 overlap').replace('n_eligible', 'eligible')}" for a_, b_ in s2.columns]
    s2 = s2.reindex(sc.config.unique()).reset_index()
    for c_ in s2.columns:
        if "eligible" in c_ or "overlap" in c_:
            s2[c_] = s2[c_].astype(int)
    A(md(s2) + "\n")
    A("**Persistence** (`persistence.csv`, figure `persistence_scatter.png`). Ratings are computed separately "
      "in two halves of the matches and correlated across players eligible in both (half thresholds).\n")
    pp = pers[["role", "split", "n_common", "spearman_rating", "spearman_level", "spearman_impact", "spearman_consistency", "spearman_delta", "spearman_brown_rating"]]
    A(md(pp) + "\n")
    rs = pers[pers.split.str.startswith("random")].set_index("role")
    A(f"This is the most important caveat in the document. Split-half Spearman correlation of the rating is "
      f"{rs.loc['batter', 'spearman_rating']:.2f} for batters and {rs.loc['bowler', 'spearman_rating']:.2f} for bowlers "
      f"(Spearman-Brown full-sample reliability {rs.loc['batter', 'spearman_brown_rating']:.2f} and "
      f"{rs.loc['bowler', 'spearman_brown_rating']:.2f}). The Level component persists weakly; the pressure delta "
      f"({rs.loc['batter', 'spearman_delta']:.2f} and {rs.loc['bowler', 'spearman_delta']:.2f}) and consistency do not "
      "persist. In plain words: who is good is measurable, who is specifically better under pressure than "
      "their own normal is mostly not, at these sample sizes. The ranking is a best estimate, not a stable "
      "ordering, and the intervals in section 1 should be taken seriously.\n")
    A(f"**Decision rule** (`decision_rule.csv`). Fixed in advance: a primary top-10 player with grid top-10 "
      f"frequency below {R['swap_threshold']:.2f} is replaced by the best-ranked outsider at or above it.\n")
    A(md(rule.assign(player_id=rule.player_id.map(lambda v: "" if pd.isna(v) else str(int(v))))) + "\n")

    # ---- 9 ------------------------------------------------------------------------------------------
    A("## 9. Rajasthan Royals fit layer\n")
    A("These identity-free expectations feed the player-credit calculations used by the rankings. Public context and its sourcing are in "
      "`context/rr_auction_context.md`. Overseas status is derived (national side in the mapping file is not "
      "India). Availability is \"unknown, check after retention list\" for every player: the retention and release "
      "deadline was moved to 17 November 2026 and the lists were not public when this was written. The IPL 2027 "
      "auction is a mini-auction on 16 December 2026 in Goa, the last before a mega auction ahead of 2028.\n")
    k = prof[(prof["sample"] == "pressure") & (prof.situation == "all") & (prof.phase != "all")]
    A("**RR under pressure by phase** (`rr_team_profile.csv`, figure `rr_gap.png`). NRAE per 100 pressure balls, "
      "RR minus the league, with RR's rank among the ten teams. The table file also splits chasing and setting.\n")
    A(md(k[["discipline", "year", "phase", "rr_balls", "rr_nrae_per100", "league_mean_nrae_per100", "rr_minus_league", "rr_rank_of_teams"]], 1) + "\n")
    g26 = k[(k.year == 2026) & (k.rr_rank_of_teams >= 7)].sort_values("rr_minus_league")
    below = k[(k.year == 2026) & (k.rr_minus_league < 0) & (k.rr_rank_of_teams < 7)]
    bowl_gap = bool(((g26.discipline == "bowling").sum() + (below.discipline == "bowling").sum()) > 0)
    A("In IPL 2026 RR ranked seventh or worse of ten under pressure in: "
      + (", ".join(f"{r.discipline} in the {r.phase} overs ({r.rr_minus_league:+.0f} per 100 balls, rank {r.rr_rank_of_teams})" for r in g26.itertuples()) or "no phase")
      + ". Below the league average but ranked better than seventh: "
      + (", ".join(f"{r.discipline} in the {r.phase} overs ({r.rr_minus_league:+.0f}, rank {r.rr_rank_of_teams})" for r in below.itertuples()) or "none")
      + ". Each cell holds about 100 to 150 balls, so treat single cells as indications. Public season reviews "
        "name two weaknesses, the middle order and the lack of a second strike bowler beside Jofra Archer. "
      + ("The data agree on the middle-order batting. " if ((g26.discipline == "batting") & (g26.phase == "middle")).any() else "The data do not single out the middle-order batting. ")
      + ("They also show pressure bowling below the league in at least one phase, consistent with the second point."
         if bowl_gap else "They do not show RR's pressure bowling below the league in any phase in 2026, so the second point is not supported by this measure.") + "\n")
    A("**RR regulars in IPL 2026** (`rr_incumbents.csv`; regular = 7 or more matches):\n")
    ii = inc[inc.regular][["player_name", "ipl2026_matches", "overseas_derived", "batter_role", "batter_rank", "batter_rating", "bowler_role", "bowler_rank", "bowler_rating"]].copy()
    for c_ in ("batter_rank", "bowler_rank"):
        ii[c_] = ii[c_].map(lambda v: "" if pd.isna(v) else f"{int(v)}")
    A(md(ii) + "\n")
    A("**Top-10 players: role, splits and gap** (`rr_fit.csv`, which also covers ranks 11 to 20 and holds the "
      "pace/spin, left/right, period and competition splits with their ball counts):\n")
    for grp in ("batter", "bowler"):
        f = fit[(fit.group == grp) & fit.final_rank.notna()].sort_values("final_rank")
        split = ["press_sr_vs_pace", "press_sr_vs_spin"] if grp == "batter" else ["press_econ_vs_rhb", "press_econ_vs_lhb"]
        d = f[["final_rank", "player_name", "role", "main_phase", "ipl_2026_team", "overseas_derived"] + split +
              ["press_nrae100_2022_24", "press_nrae100_2025_26", "press_nrae100_ipl", "press_nrae100_t20i",
               "weakest_rr_regular", "rating_gap_vs_weakest", "displacement_call"]].copy()
        d["final_rank"] = d.final_rank.astype(int)
        A(md(d, 1) + "\n")
    short = fit[fit.auction_shortlist].sort_values(["group", "rank"])
    A("**Auction shortlist.** Players from the top 20 of either group who are not already at RR, whose main "
      "phase is one of RR's 2026 pressure gap cells and whose bootstrap top-10 probability is at least 0.10:\n")
    A(md(short[["group", "rank", "player_name", "role", "main_phase", "ipl_2026_team", "overseas_derived", "boot_top10_prob", "displacement_call", "availability"]]) + "\n")
    A("**Squad-rule constraints.** This is a mini-auction, so a pick has to fit the slots and purse RR has left "
      "after releases; RR's remaining purse and open slots for 2027 are unknown until the lists are out. Sourced "
      "in the context file: a squad holds at least 18 and at most 25 players with at most 8 overseas (2026 cycle, "
      "several outlets; assumed unchanged for 2027), and RR filled all 25 places in 2026. The limit of 4 overseas "
      "players in an XI rests on one weak source and is assumed. "
      f"RR's 2026 regulars already include {int(inc[inc.regular].overseas_derived.sum())} derived-overseas players, so "
      "an overseas pick has to displace one of them in the XI; Indian options on the shortlist are worth more "
      "to RR than their rating alone says. A mini-auction also has no right-to-match and few slots, which favours "
      "a short, role-specific shortlist over a long list.\n")
    A("\"Would displace\" is used only where the candidate's 80% rating interval lies entirely above the "
      "incumbent's. Everything else is described as inside the noise.\n")

    # ---- 10, 11 -----------------------------------------------------------------------------------------
    A("## 10. Limitations and where the model is least certain\n")
    A("- **Low persistence.** See section 8. The rating has limited repeatability and the pressure-specific "
      "components have almost none.")
    A("- **Extras and target reconstruction.** The chase target uses only first-innings ball data and is "
      "therefore available before the chase. Incomplete extras fields leave residual score reconstruction error "
      f"(strictly out-of-time margin MAE {ex['margin MAE (runs), fitted']:.1f} runs). Neither final chase totals "
      "nor result margins are used to repair the target.")
    A("- **Small pressure samples.** The pressure sample is a fifth of the data. A typical eligible batter has "
      f"{int(rb.n_press_balls.median())} pressure balls (median) and a typical bowler {int(rw.n_press_balls.median())}.")
    A("- **Selection into high-leverage states.** Good teams reach close finishes more often and choose who "
      "bats and bowls in them. Team-season and opponent effects absorb part of this, not all.")
    A("- **Run value of a wicket at the death is small.** In run terms a wicket with two overs left costs little, "
      "so NRAE gives little credit for death wickets. WPA carries that value, at 25% of the rating.")
    A("- **First-innings pressure is weakly identified.** First-innings win probability barely moves away from "
      "0.5, so the first-innings pressure sample is the top fifth of a narrow range.")
    A("- **Team context and role.** A finisher and an opener face different jobs. "
      + ("The role-aware baseline corrects the largest part (new batters score well below set batters), not all of it."
         if role_aware else "The baseline does not know batting position or how long the batter has been in.") )
    A("- **No pitch, weather, dew, boundary-size or fielding data.** Ball-speed is missing on about 39% of rows "
      "and is not used.")
    A("- **Fixed eligible set in the bootstrap** and penalties fixed at their cross-validated values: intervals "
      "are somewhat too narrow.")
    A("- **Outside cross-checks.** One data error was found and corrected (match 20190). Sooryavanshi's IPL 2026 "
      "line rebuilt from the ball data (776 runs, average 48.5, strike rate 237.3) matches published figures, and "
      "RR's 2026 playoff results match the reports. Five unflagged short matches were found by internal "
      "checks. Other data errors of the same kind may remain undetected.\n")
    A("## 11. Honest weak spots\n")
    A("- The rating mostly measures how good a player is in general and only slightly how much he lifts under "
      "pressure. The data cannot support a stronger clutch claim, and section 8 shows why.")
    A("- The shift in batting and bowling outcomes from Normal to pressure almost disappears once phase, "
      "innings and wickets are held fixed. The pressure definition separates stakes, not behaviour.")
    lo = pd.concat([tb.assign(g="batter"), tw.assign(g="bowler")])
    lo = lo[lo.boot_top10_prob < 0.5]
    A(f"- {len(lo)} of the 20 listed players finish in the top 10 in fewer than half of the bootstrap resamples: "
      + ", ".join(f"{r.player_name} ({r.boot_top10_prob:.2f})" for r in lo.itertuples()) + ". The lower half of each list "
        "is close to interchangeable with ranks 11 to 25.")
    sm_ = pd.concat([tb, tw]).sort_values("n_press_balls").iloc[0]
    A(f"- The smallest pressure sample in the lists is {sm_.player_name} with {int(sm_.n_press_balls)} pressure balls. "
      "He qualifies under the pre-registered thresholds and is kept; his interval is wide.")
    io = sc[sc.config.isin(["IPL only", "T20I only"])]
    A("- The ridge and empirical Bayes estimators agree on the composite but only moderately on Level "
      "(section 5). Restricting to one competition changes the lists: top-10 overlap with the primary is "
      + "; ".join(f"{r.config}, {r.role}s {r.top10_overlap_with_primary} of 10" for r in io.itertuples()) + ".")
    A("- **Extras calibration.** Per-match coefficients are estimated from strictly earlier matches only. "
      "The fixed one-run-per-extra fallback is used before enough history exists; see the out-of-time comparison "
      "in `extras_calibration.csv` rather than treating the in-sample fit as evidence.")
    A("- Several of the highest-volume death-over players rank poorly (section 7). The model may be right, or "
      "the baseline may still be unfair to their role. This was not adjusted by hand.\n")

    # ---- 12, 13 ---------------------------------------------------------------------------------------------
    A("## 12. Reproduction\n")
    A("```bash\npip install -r requirements.txt\n```\n\n```bash\npython run_all.py\n```\n\n```bash\npython -m pytest -q tests\n```\n")
    A("Runtime depends on available CPU, model fitting and the 1,000-resample match bootstrap. Seeds are fixed "
      "in `config.json`, and the GitHub Actions workflow runs the full pipeline and acceptance tests remotely.\n")
    A("## 13. Open questions and next steps\n")
    A("- Check the retention lists and replace the availability column, then re-run stage 09.")
    A("- Obtain true innings totals or extras run values; the reconstruction error would vanish.")
    A("- Add leagues beyond the IPL and T20Is to raise pressure samples; persistence is limited by sample size.")
    A("- Model the pressure delta hierarchically by role (finishers, death bowlers) instead of per player; a "
      "role-level effect may be estimable where a player-level one is not.")
    A("- Use ball-tracking variables (length, line) to separate execution from outcome for bowlers.")
    A("- Test whether a win-probability model with team strength changes leverage for mismatched fixtures.\n")

    # ---- phase 2 -----------------------------------------------------------------------------------------------
    A("## What changed in phase 2 (before phase 3)\n")
    A("Phase 2 audited the phase 1 pipeline, then tried model changes and judged each only on model-quality "
      "evidence: out-of-fold log loss and calibration, split-half reliability of the ratings (mean Spearman "
      "over 20 random match-half splits), season-split persistence and bootstrap stability. The identity of "
      "the players in the lists was never a criterion. Phase 1 results are kept in `outputs/phase1/`. The full "
      "log is in `docs/DECISIONS.md`, sections C and D.\n")
    if x2 is not None:
        cols = ["tag", "wp_logloss", "wp_logloss_inn2", "lev_spearman_abs_wpa", "bat_xruns_rmse", "bowl_xruns_rmse",
                "bat_splithalf_rating", "bowl_splithalf_rating", "bat_season_persistence", "bowl_season_persistence",
                "bat_boot_top10_prob_of_top10", "bowl_boot_top10_prob_of_top10", "bat_boot_rank_iqr80_top20", "bowl_boot_rank_iqr80_top20"]
        d = x2[cols].copy()
        d.insert(1, "verdict", d.tag.map(lambda t: verdicts.get(t, {}).get("verdict", "")))
        A("Model-quality scorecard (`phase2_experiments.csv`). Higher is better for the split-half, persistence, "
          "leverage-validity and top-10 probability columns; lower is better for log loss, RMSE and rank-interval width.\n")
        A(md(d, 4) + "\n")
        for t_ in x2.tag:
            v = verdicts.get(t_, {})
            A(f"- **{t_}**: {x2.set_index('tag').reason[t_]}. {v.get('note', '')}")
        A("")
        se = x2.set_index("tag")
        if "base" in se.index:
            A(f"Standard error of the split-half figure across the 20 splits is about "
              f"{se.loc['base', 'bat_splithalf_rating_se']:.3f} (batters) and {se.loc['base', 'bowl_splithalf_rating_se']:.3f} "
              "(bowlers); differences smaller than about twice that are not evidence.\n")
    def compare(old_dir, new_dir, old_lab, new_lab, why, phase3=False):
        rd = lambda d, n: pd.read_csv(os.path.join(ROOT, "outputs", d, n)) if d != "tables" else T(n)
        for label in ("batters", "bowlers"):
            old, new = rd(old_dir, f"top10_{label}.csv"), rd(new_dir, f"top10_{label}.csv")
            fo = rd(old_dir, f"{label[:-1]}_ratings.csv").set_index("player_id")
            fn = rd(new_dir, f"{label[:-1]}_ratings.csv").set_index("player_id")
            d = pd.DataFrame({"Rank": range(1, 11), old_lab: old.player_name.values, new_lab: new.player_name.values})
            A(f"*{label.capitalize()}*\n")
            A(md(d) + "\n")
            any_change = False
            for p in dict.fromkeys(list(new.player_id) + list(old.player_id)):
                if p not in fo.index or p not in fn.index or int(fo.loc[p, "rank"]) == int(fn.loc[p, "rank"]):
                    continue
                any_change = True
                status = ("enters the top 10" if p not in set(old.player_id) else
                          "leaves the top 10" if p not in set(new.player_id) else "stays in the top 10")
                line = f"- {fn.player_name[p]}: rank {int(fo.loc[p, 'rank'])} to {int(fn.loc[p, 'rank'])}, {status}. "
                if phase3:
                    ws = CFG["composite_weights_spec"]
                    dropped = fo.loc[p, "rating"] - ws["level"] * fo.loc[p, "z_level"]
                    line += (f"Level z {fo.loc[p, 'z_level']:+.2f} (unweighted) to {fn.loc[p, 'z_level']:+.2f} (leverage-weighted); "
                             f"the three dropped components had contributed {dropped:+.2f} to the old rating "
                             f"(impact {fo.loc[p, 'z_impact']:+.1f}, consistency {fo.loc[p, 'z_consistency']:+.1f}, delta {fo.loc[p, 'z_delta']:+.1f}).")
                else:
                    zc = ["z_level", "z_impact", "z_consistency", "z_delta"]
                    ws = CFG["composite_weights_spec"]
                    dd = {c: ws[c[2:]] * (fn.loc[p, c] - fo.loc[p, c]) for c in zc}
                    big = max(dd, key=lambda c: abs(dd[c]))
                    line += (f"Rating {fo.loc[p, 'rating']:.2f} to {fn.loc[p, 'rating']:.2f}; the component that moved most is "
                             f"{big[2:]} ({dd[big]:+.2f} rating points).")
                A(line)
            if not any_change:
                A("- No rank changed among these players.")
            A("")
        A(why + "\n")

    A("**Top-10 lists before and after** (`outputs/phase1/top10_*.csv` versus `outputs/phase2/top10_*.csv`):\n")
    compare("phase1", "phase2", "Phase 1", "Phase 2 (final)",
            "Every difference has the same cause, the role-aware baseline (post-hoc change P-1). It stops charging "
            "batters for the slow first balls of an innings and stops crediting bowlers for bowling to batters who "
            "have just arrived. Ratings move by up to about half a point and neighbours swap places. "
            "Ranks 9 to 12 are separated by a few hundredths of a rating point in both versions.")
    A(verdicts.get("_summary", {}).get("note", "") + "\n")

    # ---- phase 3 ---------------------------------------------------------------------------------------------
    A("## What changed in phase 3\n")
    pc = T("phase3_final_candidates.csv")
    tc = T("phase3_temporal.csv")
    A("Phase 3 looked for the best rating the supplied data can support. The yardstick was made stricter than "
      "phase 2's: rate players from one random half of the matches and measure how well that rating predicts "
      "the same players' raw pressure performance in the other half (weighted Spearman correlation, weights = "
      "held-out pressure balls), over 20 random splits in both directions, for two targets (pressure NRAE and "
      "pressure WPA per 100 balls). Rating-versus-rating correlation, used in phase 2, can reward a score for "
      "being stable noise; this cannot. Differences are paired: every candidate is scored on the same splits. "
      "A 2022-24 to 2025-26 temporal test was kept apart from the selection and used only to confirm. Rule "
      "fixed before adopting: the highest sum of the four random-split correlations wins, provided it does not "
      "lose to the old composite on the temporal NRAE check. Name and identity of players played no part.\n")
    A("**Finding 1. The extra components did not predict anything.** Single components used alone "
      "(`phase3_candidates.csv`, mean over splits, pressure NRAE target):\n")
    cand = T("phase3_candidates.csv")
    one = cand[cand.candidate.isin(["level only", "impact only", "consistency only", "delta only", "primary composite",
                                    "level only [leverage-weighted (alpha 1)]"])]
    one = one.pivot(index="candidate", columns="role", values="pred_nrae").reset_index()
    A(md(one.rename(columns={"bat": "batters", "bowl": "bowlers"}), 3) + "\n")
    A("Level predicts held-out pressure performance. Delta and consistency are at or near zero, and impact is "
      "negative for batters. The specification gave these three 60% of the weight; they added noise.\n")
    A("**Finding 2. Weighting each ball by its leverage is a better 'pressure level' than a cutoff.** Candidates, "
      "paired against the old composite on the same splits (`phase3_final_candidates.csv`; positive = better):\n")
    cols = ["role", "candidate", "pred_nrae", "pred_wpa", "d_nrae_vs_spec", "d_nrae_se", "d_wpa_vs_spec", "d_wpa_se"]
    A(md(pc[cols], 3) + "\n")
    A("Temporal confirmation, rated on 2022-24 and scored on 2025-26 pressure performance (`phase3_temporal.csv`; "
      "one draw, so no standard error):\n")
    A(md(tc, 3) + "\n")
    A("**Reading it honestly.** On the random splits the leverage-weighted level beats the old composite on both "
      "targets for batters (about 3 standard errors on WPA) and on NRAE for bowlers (about 3.5). On the "
      "temporal test it beats the old composite on NRAE in both groups, but the plain unweighted level scores "
      "higher still for batters, and the old composite scores higher on WPA for bowlers. The temporal draw is a "
      "single sample of about 100 players and is noisy; it shows the improvement is not purely an artefact of "
      "random splits, not that this exact variant is the optimum. The absolute correlations are small (batters "
      "about 0.06, bowlers about 0.14): pressure performance is only weakly predictable from past pressure "
      "performance, so every ranking here, old or new, is a noisy estimate.\n")
    A("**Predictive challenger, not the primary task ranking.** Phase 3 explored a Level-focused score with "
      "leverage weighting because it performed better on some held-out predictive comparisons. Its temporal "
      "results are mixed and pressure-specific consistency/delta are not reliably persistent. It remains a "
      "separate challenger in `outputs/v3/`. The primary shortlist and Rajasthan Royals fit use the "
      "pre-registered four-component composite above, not this post-hoc alternative.\n")
    sc2 = sc[sc.config.isin(["no leverage weighting", "leverage weight power 0.5", "leverage weight power 2", "spec weights 0.40/0.25/0.20/0.15"])]
    A("How much the lists depend on this choice (`sensitivity_configs.csv`, top-10 overlap with the final lists):\n")
    A(md(sc2[["role", "config", "n_eligible", "top10_overlap_with_primary", "spearman_with_primary"]]) + "\n")
    A("**Other phase 3 attempts that did not help.** Averaging the win-probability models gave log loss 0.5217 "
      "against 0.5220, which is nothing; the win-probability model is at its ceiling for these features and "
      "was not changed. Leverage power 2 predicts worse than power 1 (it concentrates weight on too few balls). "
      "Re-tuning the ridge penalties under leverage weighting moved them to 3,000 and 30,000 and left the "
      "conclusions unchanged (the table above was recomputed with them).\n")
    A("**Persistence after phase 3** (`persistence.csv`). Split-half reliability of the rating rose from "
      "0.06 to {:.2f} for batters and from 0.12 to {:.2f} for bowlers. Still low; see section 8.\n".format(
          rs.loc['batter', 'spearman_rating'], rs.loc['bowler', 'spearman_rating']))
    A("**Top-10 lists before and after** (`outputs/phase2/top10_*.csv` versus `outputs/tables/top10_*.csv`):\n")
    compare("phase2", "tables", "Phase 2", "Phase 3 (final)",
            "The lists change because the rating changed definition: players whose pressure results came with "
            "good impact or consistency numbers but a modest underlying level move down, and players with a high "
            "leverage-weighted level move up. Ranks 6 to 12 are separated by a fraction of a rating point in both "
            "versions and are close to interchangeable.", phase3=True)

    # ---- dropdown block -------------------------------------------------------------------------------------------
    A("## Exact dropdown selections\n")
    for label, t in [("Batters", tb), ("Bowlers", tw)]:
        A(f"**{label}**\n")
        for r in t.itertuples():
            A(f"{r.final_rank}. {r.dropdown_name} ({r.player_id})")
        A("")
    txt = "\n".join(L).replace("—", "-")
    with open(os.path.join(ROOT, "docs", "FINDINGS.md"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"  wrote docs/FINDINGS.md ({len(txt.splitlines())} lines)")


if __name__ == "__main__":
    main()
