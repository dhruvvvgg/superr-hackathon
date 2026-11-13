"""V3 stage D: final comparison table, figures and docs/V3_FINDINGS.md, from outputs/v3 and outputs/v2."""
import json
import os

import numpy as np
import pandas as pd

from common import ROOT, TABLES, setup_matplotlib

V3 = os.path.join(ROOT, "outputs", "v3")
V2 = os.path.join(ROOT, "outputs", "v2")
R3 = lambda n: pd.read_csv(os.path.join(V3, n))


def md(df, nd=3):
    d = df.copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else f"{v:.{nd}f}")
        elif d[c].dtype == bool:
            d[c] = d[c].map({True: "yes", False: "no"})
    d = d.fillna("").astype(str)
    return "\n".join(["| " + " | ".join(d.columns) + " |", "|" + "|".join("---" for _ in d.columns) + "|"] +
                     ["| " + " | ".join(r) + " |" for r in d.values])


def final_comparison():
    """Paired V3 versus V2 on the identical trials, plus naive statistics from V2's confirm table."""
    rows = []
    src = {"bat": ("_trials_score_xfeat_bat.csv", "base"), "bowl": ("_trials_score_main_bowl.csv", "base")}
    for role in ("bat", "bowl"):
        v3 = R3(src[role][0])
        v2 = R3(f"_trials_combine_main_{role}.csv")
        for kind, lab in [("tune", "tuning trials"), ("conf", "confirmation trials")]:
            a, b = v3[v3.kind == kind][src[role][1]].values, v2[v2.kind == kind]["v2 base"].values
            d = a - b
            rows.append(dict(role=role, trials=lab, v3=a.mean(), v2=b.mean(), gain=d.mean(), gain_se=d.std() / np.sqrt(len(d)),
                             gain_z=d.mean() / (d.std() / np.sqrt(len(d))), n_trials=len(d)))
    return pd.DataFrame(rows)


def main():
    print("V3 stage D: report")
    plt = setup_matplotlib()
    top = {k: R3(f"top10_{k}.csv") for k in ("batters", "bowlers")}
    fc = final_comparison()
    expected_metrics = pd.read_csv(os.path.join(TABLES, "expected_model_metrics.csv"))
    wp_metrics = pd.read_csv(os.path.join(TABLES, "wp_model_metrics.csv"))
    wp_bins = pd.read_csv(os.path.join(TABLES, "wp_calibration_bins.csv"))
    fc.to_csv(os.path.join(V3, "final_comparison.csv"), index=False, float_format="%.5f")
    conf2 = pd.read_csv(os.path.join(V2, "confirm.csv"))
    st, cb, sc = R3("structure.csv"), R3("combine.csv"), R3("score.csv")
    chosen = json.load(open(os.path.join(V3, "chosen_config.json")))

    for label, color in [("batters", "#1f6fb2"), ("bowlers", "#2a9d8f")]:
        t = top[label].iloc[::-1]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.barh(t.player_name, t.rating, color=color, alpha=0.85)
        ax.errorbar(t.rating, t.player_name, xerr=[np.maximum(t.rating - t.boot_rating_p10, 0), np.maximum(t.boot_rating_p90 - t.rating, 0)],
                    fmt="none", ecolor="black", capsize=4, lw=1.4)
        for y_, (r_, p_) in enumerate(zip(t.boot_rating_p90, t.boot_top10_prob)):
            ax.text(r_ + 0.3, y_, f"P(top 10) {p_:.2f}", va="center", fontsize=10)
        ax.set_xlabel("Runs per 100 balls above an average player in the same situation (80% bootstrap interval)")
        ax.set_title(f"Final (V3): top 10 {label} under pressure")
        ax.set_xlim(0, t.boot_rating_p90.max() * 1.35)
        fig.tight_layout(); fig.savefig(os.path.join(V3, f"v3_top10_{label}.png")); plt.close(fig)
    c2 = conf2[conf2.trials == "confirmation trials"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, (role, lab) in zip(axes, [("bat", "Batters"), ("bowl", "Bowlers")]):
        f = fc[(fc.role == role) & (fc.trials == "confirmation trials")].iloc[0]
        d = c2[c2.role == role].set_index("method")
        items = [("V3 (final)", f.v3), ("V2", f.v2)] + [(m, d.loc[m, "objective"]) for m in d.index if m.startswith("raw")]
        ax.barh([i[0] for i in items][::-1], [i[1] for i in items][::-1],
                color=["#d1495b" if i[0].startswith("V3") else "#9ecae1" for i in items][::-1])
        ax.set_title(lab); ax.set_xlabel("Held-out predictive correlation (confirmation trials)"); ax.axvline(0, color="black", lw=1)
    fig.suptitle("Predicting later pressure performance: final model against V2 and raw statistics")
    fig.tight_layout(); fig.savefig(os.path.join(V3, "v3_confirmation.png")); plt.close(fig)

    L = []; A = L.append
    A("# Final model (V3): who delivers under pressure\n")
    A("This is the recommended candidate model. It is V2 (`docs/V2_FINDINGS.md`) extended with a pace interaction "
      "for batters and stronger shrinkage of the wicket component for bowlers. Candidate adoption is based on "
      "the tuning trials only (paired z > 2). The legacy confirmation trials are shown as diagnostics, not as "
      "an untouched holdout: earlier V3 iterations used them for candidate gating. All tables are in `outputs/v3/`.\n")
    A("## 1. Result\n")
    A("Rating: leverage-weighted, opponent-adjusted NRAE per 100 balls, shrunk toward average for small samples. "
      "It estimates overall performance on high-leverage deliveries relative to an identity-free expected-value "
      "baseline. It is not a causal estimate of how much a player improves under pressure versus their own "
      "normal level, and it is not a consistency score. The interval is the 80% interval over 1,000 match resamples. "
      "Raw pressure-versus-normal strike-rate/economy contrasts and pressure-innings dispersion are supplied "
      "as descriptive diagnostics; they do not change the ranking.\n")
    for label in ("batters", "bowlers"):
        t = top[label]
        A(f"### Top 10 {label} (`outputs/v3/top10_{label}.csv`)\n")
        d = pd.DataFrame({"Rank": t.final_rank, "Player (id)": [f"{n} ({i})" for n, i in zip(t.player_name, t.player_id)],
                          "Rating": t.rating, "80% interval": [f"{a:.1f} to {b:.1f}" for a, b in zip(t.boot_rating_p10, t.boot_rating_p90)],
                          "80% rank interval": [f"{a:.0f} to {b:.0f}" for a, b in zip(t.boot_rank_p10, t.boot_rank_p90)],
                          "P(top 10)": t.boot_top10_prob, "Pressure balls": t.n_press_balls})
        A(md(d, 2) + "\n")
        for r in t.itertuples():
            if label == "batters":
                A(f"{r.final_rank}. **{r.player_name}**: {r.runs_part:+.1f} from scoring and {r.wicket_part:+.1f} from not getting out "
                  f"(per 100 balls); strike rate {r.press_sr:.0f} under pressure against {r.normal_sr:.0f} otherwise, "
                  f"{int(r.press_runs)} runs and {int(r.press_outs)} dismissals in {int(r.n_press_balls)} pressure balls.")
            else:
                A(f"{r.final_rank}. **{r.player_name}**: {r.runs_part:+.1f} from runs saved and {r.wicket_part:+.1f} from wickets "
                  f"(per 100 balls); economy {r.press_econ:.2f} under pressure against {r.normal_econ:.2f} otherwise, "
                  f"{int(r.press_wkts)} wickets in {int(r.n_press_balls)} pressure balls.")
        A(f"\nFigure: `outputs/v3/v3_top10_{label}.png`.\n")
    A("## 2. Predictive comparison with V2 (legacy confirmation is descriptive only)\n")
    A(md(fc.assign(role=fc.role.map({"bat": "batters", "bowl": "bowlers"})), 4) + "\n")
    cb_ = c2.set_index(["role", "method"]).objective
    A(f"For comparison on the confirmation trials, raw pressure strike rate scores {cb_[('bat', 'raw strike rate')]:.3f} for "
      f"batters and raw pressure economy {cb_[('bowl', 'raw economy (negated)')]:.3f} for bowlers. Figure: `outputs/v3/v3_confirmation.png`.\n")
    A("## 3. What changed from V2, and the evidence\n")
    A("1. **Bowlers: the wicket part of the rating is shrunk ten times harder than the runs part.** Wickets under "
      "pressure are rare and noisy; run prevention is far more repeatable. Giving each its own shrinkage lets the "
      "rating keep the repeatable part.")
    A("2. **Batters: a shrunk pace-versus-spin adjustment.** Each batter gets a small, heavily shrunk extra effect "
      "against pace, applied in proportion to how much pace he faces.")
    A("3. **Batters: a richer situational baseline.** Expected runs and dismissal also know recent momentum, the "
      "dot-ball streak, live win probability, ball position in the over, partnership length and the bowler's "
      "workload. Same features did not help bowlers (worse on confirmation), so the bowler baseline is unchanged.\n")
    A("Chosen configuration (`outputs/v3/chosen_config.json`):\n")
    A(md(pd.DataFrame([dict(group=k, **{kk: vv for kk, vv in v.items() if kk != "evidence"}) for k, v in chosen.items()]), 2) + "\n")
    A("### Every variant tried (paired difference against the current base; adoption uses tuning z > 2 only)\n")
    keep = ["role", "candidate", "tune_diff", "tune_z", "conf_diff", "conf_z", "passes"]
    A("**Round 1, structure** (`structure.csv`, base = V2):\n")
    A(md(st[keep]) + "\n")
    A("**Round 2, combinations on the round-1 winners** (`combine.csv`):\n")
    A(md(cb[keep]) + "\n")
    A("**Round 3, how the score is formed** (`score.csv`, richer-baseline credit for batters is in `score_xfeat.csv`):\n")
    A(md(sc[keep]) + "\n")
    bo = [pd.read_csv(os.path.join(V3, f"_trials_baseonly_{t}_{r}.csv")) for t in ("main", "xfeat") for r in ("bat", "bowl")]
    rows = []
    for i, r in enumerate(("bat", "bowl")):
        a, b = bo[i], bo[2 + i]
        for k in ("tune", "conf"):
            d = b[b.kind == k].base.values - a[a.kind == k].base.values
            rows.append(dict(role=r, trials=k, richer_baseline_gain=d.mean(), se=d.std() / np.sqrt(len(d))))
    A("**Richer baseline, same model on both credit tables** (`_trials_baseonly_*.csv`):\n")
    A(md(pd.DataFrame(rows), 4) + "\n")
    A("**Tried and rejected in this phase:** ensembles of configurations (all worse), leverage floors and caps, "
      "separate opponent penalties, death-overs and left-hander interaction terms, re-weighting the wicket part of the "
      "score, and blending in win-probability impact. A leverage cap of 3 for batters came close (positive on both "
      "trial sets, tuning z about 1.2 to 1.5) and was not adopted under the rule.\n")
    A("## 4. How the final lists compare\n")
    v2t = {k: pd.read_csv(os.path.join(V2, f"top10_{k}.csv")) for k in ("batters", "bowlers")}
    p3 = {k: pd.read_csv(os.path.join(TABLES, f"top10_{k}.csv")) for k in ("batters", "bowlers")}
    for k in ("batters", "bowlers"):
        a = set(top[k].player_id)
        new2 = top[k][~top[k].player_id.isin(v2t[k].player_id)].player_name.tolist()
        out2 = v2t[k][~v2t[k].player_id.isin(top[k].player_id)].player_name.tolist()
        A(f"- {k.capitalize()}: {len(a & set(v2t[k].player_id))} of 10 shared with V2, {len(a & set(p3[k].player_id))} of 10 with phase 3. "
          f"In against V2: {', '.join(new2) or 'none'}; out: {', '.join(out2) or 'none'}.")
        d = pd.DataFrame({"Rank": range(1, 11), "V2": v2t[k].player_name.values, "Final (V3)": top[k].player_name.values})
        A("\n" + md(d) + "\n")
    A("## 5. Limits, stated plainly\n")
    fcb = fc[(fc.role == "bat") & (fc.trials == "confirmation trials")].iloc[0]
    fcw = fc[(fc.role == "bowl") & (fc.trials == "confirmation trials")].iloc[0]
    A(f"- Prediction is modest: held-out correlation about {fcb.v3:.2f} for batters and {fcw.v3:.2f} for bowlers. Batting under "
      "pressure is much less predictable than bowling under pressure in this data.")
    A("- The batter interaction is a modest tuning-set result and is vulnerable to multiple-comparison optimism "
      "after about 30 variants. The bowler shrinkage change has a larger tuning-set gain. Legacy confirmation "
      "numbers are not independent evidence because they were used in earlier V3 gating.")
    A("- Ranks 6 to 10 of the batters overlap heavily with ranks 11 to 20 (see the rank intervals).")
    A("- The initial warm-up period is cross-fitted internally by match; every subsequent WP, leverage, pressure, "
      "resource-value and expected-value fold is trained only on earlier dates. Venue averages and ridge "
      "penalty CV are also past-only. The temporal table below therefore evaluates a chronologically cross-fit "
      "pipeline after the warm-up period; it is still a diagnostic, not a separately reserved model-selection holdout.")
    for role in ("batter", "bowler"):
        xr = expected_metrics[expected_metrics.model == f"{role} xRuns"].iloc[0]
        wk = expected_metrics[expected_metrics.model == f"{role} xWkt"].iloc[0]
        wk_candidate = expected_metrics[expected_metrics.model == f"{role} xWkt candidate"].iloc[0]
        A(f"- {role.capitalize()} expected runs: OOF RMSE {xr.oof:.3f} versus fold-local phase-mean {xr.phase_mean_baseline:.3f}. "
          f"Expected wickets use the fold-local innings/phase mean (log loss {wk.oof:.4f}); the calibrated LightGBM candidate "
          f"remains diagnostic only (log loss {wk_candidate.oof:.4f}) because the simpler baseline is the selected reference.")
    wp_primary = wp_metrics[(wp_metrics.role == "primary") & (wp_metrics["sample"] == "all")].iloc[0]
    outside = int((~wp_bins.gap_within_2sd).sum())
    A(f"- Win-probability OOF log loss is {wp_primary.log_loss:.4f}; maximum dense-bin calibration gap is "
      f"{wp_primary.max_calib_gap_dense_bins:.3f}, with {outside} of {len(wp_bins)} bins outside the match-bootstrap 2-SD band. "
      "Calibration remains a reported diagnostic, not a claim of perfect calibration.")
    A("- No pitch, weather, dew, fielding or ball-tracking data; bye and leg-bye run values are not recorded.")
    A("- Availability for the auction is unknown until retention lists are published.\n")
    A("## 6. Forward-in-time validation\n")
    tv = pd.read_csv(os.path.join(V3, "temporal_validation.csv"))
    keep_tv = ["role", "cutoff", "n_train_matches", "n_test_matches", "n_players", "nrae_corr", "wpa_corr", "objective", "train_max_date", "test_min_date"]
    A(md(tv[keep_tv], 4) + "\n")
    A("Each row fits the V3 rating on matches before the cutoff and scores the same players on the following "
      "six/seven months. Upstream state and credit features are now generated by warm-up cross-fitting and "
      "forward-only chronological folds; no later match is used to construct a test-fold WP, leverage, pressure, "
      "resource-value, expected-value or venue feature. These windows remain diagnostic rather than a reserved "
      "final holdout because the broader V3 tuning process has already examined overlapping historical periods.\n")
    A("## 7. Reproduce\n")
    A("```bash\npython run_all.py\n```\n")
    A("Stages 31 (richer batter baseline), 30 (all experiment rounds), 32 (ratings), 35 (forward-only validation), 33 (report) and 34 (V3 RR fit).\n")
    A("## 8. Exact dropdown selections\n")
    for k in ("batters", "bowlers"):
        A(f"**{k.capitalize()}**\n")
        for r in top[k].itertuples():
            A(f"{r.final_rank}. {r.dropdown_name} ({r.player_id})")
        A("")
    txt = "\n".join(L).replace("—", "-")
    open(os.path.join(ROOT, "docs", "V3_FINDINGS.md"), "w", encoding="utf-8").write(txt)
    print(f"  wrote docs/V3_FINDINGS.md ({len(txt.splitlines())} lines)")
    print(fc.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
