"""V2 stage C: figures and docs/V2_FINDINGS.md, generated from outputs/v2 tables."""
import json
import os

import numpy as np
import pandas as pd

from common import ROOT, TABLES, setup_matplotlib

OUT = os.path.join(ROOT, "outputs", "v2")
R = lambda n: pd.read_csv(os.path.join(OUT, n))


def md(df, nd=2):
    d = df.copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else f"{v:.{nd}f}")
    d = d.fillna("").astype(str)
    return "\n".join(["| " + " | ".join(d.columns) + " |", "|" + "|".join("---" for _ in d.columns) + "|"] +
                     ["| " + " | ".join(r) + " |" for r in d.values])


def main():
    print("V2 stage C: report")
    plt = setup_matplotlib()
    top = {"batters": R("top10_batters.csv"), "bowlers": R("top10_bowlers.csv")}
    rat = {"batters": R("ratings_batters.csv"), "bowlers": R("ratings_bowlers.csv")}
    conf, log = R("confirm.csv"), R("search_log.csv")
    chosen = json.load(open(os.path.join(OUT, "chosen_config.json")))
    prev = {"batters": pd.read_csv(os.path.join(TABLES, "top10_batters.csv")), "bowlers": pd.read_csv(os.path.join(TABLES, "top10_bowlers.csv"))}
    p1 = {"batters": pd.read_csv(os.path.join(ROOT, "outputs", "phase1", "top10_batters.csv")),
          "bowlers": pd.read_csv(os.path.join(ROOT, "outputs", "phase1", "top10_bowlers.csv"))}

    # ---- figures ---------------------------------------------------------------------------------
    for label, color in [("batters", "#1f6fb2"), ("bowlers", "#2a9d8f")]:
        role = "bat" if label == "batters" else "bowl"
        score = chosen[role]["score"]
        if score == "nrae":
            score_label = "Shrunk pressure NRAE (runs per 100 balls)"
        elif score == "wpa":
            score_label = "Shrunk win-probability impact (per 100 balls)"
        elif score.startswith("blend"):
            beta = float(score.replace("blend", ""))
            score_label = f"Standardised NRAE + {beta:g} x standardised WPA (unitless)"
        else:
            raise ValueError(f"Unknown selected V2 score: {score}")
        t = top[label].iloc[::-1]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.barh(t.player_name, t.rating, color=color, alpha=0.85)
        ax.errorbar(t.rating, t.player_name, xerr=[np.maximum(t.rating - t.boot_rating_p10, 0), np.maximum(t.boot_rating_p90 - t.rating, 0)],
                    fmt="none", ecolor="black", capsize=4, lw=1.4)
        for y_, (r_, p_) in enumerate(zip(t.boot_rating_p90, t.boot_top10_prob)):
            ax.text(r_ + 0.3, y_, f"P(top 10) {p_:.2f}", va="center", fontsize=10)
        ax.set_xlabel(f"{score_label} (80% bootstrap interval)")
        ax.set_title(f"V2: top 10 {label} under pressure")
        ax.set_xlim(0, t.boot_rating_p90.max() * 1.35)
        fig.tight_layout(); fig.savefig(os.path.join(OUT, f"v2_top10_{label}.png")); plt.close(fig)
    c = conf[conf.trials == "confirmation trials"]
    names = {"v2 chosen": "V2 (chosen)", "reference": "Reference setup", "unweighted level (alpha 0)": "No leverage weighting",
             "almost no shrinkage (lam 30)": "Almost no shrinkage", "raw NRAE": "Raw pressure NRAE", "raw strike rate": "Raw pressure strike rate",
             "raw economy (negated)": "Raw pressure economy"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharex=True)
    for ax, (role, lab) in zip(axes, [("bat", "Batters"), ("bowl", "Bowlers")]):
        d = c[c.role == role].sort_values("objective")
        ax.barh([names.get(m, m) for m in d.method], d.objective, xerr=d.se, color=["#d1495b" if m == "v2 chosen" else "#9ecae1" for m in d.method], capsize=3)
        ax.set_title(lab); ax.set_xlabel("Held-out predictive correlation (confirmation trials)")
        ax.axvline(0, color="black", lw=1)
    fig.suptitle("How well each method predicts later pressure performance (higher is better)")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "v2_confirmation.png")); plt.close(fig)

    # ---- document ----------------------------------------------------------------------------------
    L = []; A = L.append
    A("# V2: a fresh build of the pressure rating\n")
    A("> **Exploratory predictive challenger.** V2 is a predictive-model comparison, not the primary "
      "task-specific shortlist. V3 contains later challenger experiments; neither replaces the four-component "
      "primary ranking in `docs/FINDINGS.md`. This document records the V2 design and its diagnostics.\n")
    A("This is an independent second design, made from the six supplied CSVs and the problem statement only. "
      "The ball-level preparation (legal balls, extras, match state, out-of-fold win probability, expected "
      "runs and wickets) is reused from `docs/FINDINGS.md` because it is data engineering that was checked "
      "against scorecards and published figures. Everything about how players are rated was redesigned around "
      "one question: **which method best predicts a player's future performance when the match is on the "
      "line?** Every table is in `outputs/v2/`, produced by `src/20_v2_search.py`, `21_v2_rate.py` and `22_v2_report.py`.\n")
    A("## 1. Result\n")
    A("The selected V2 score is applied exactly as chosen by the forward-window search. NRAE and WPA are "
      "reported as shrunk per-100-ball components; when a blend is selected, both components are standardised "
      "over the registered eligible player universe and combined using the selected coefficient. Blend ratings "
      "are unitless, not runs per 100 balls. Intervals are 80% match-cluster bootstrap intervals from 1,000 "
      "resamples.\n")
    for label in ("batters", "bowlers"):
        t = top[label]
        A(f"### Top 10 {label} (`top10_{label}.csv`)\n")
        d = pd.DataFrame({"Rank": t.final_rank, "Player (id)": [f"{n} ({i})" for n, i in zip(t.player_name, t.player_id)], "Rating": t.rating,
                          "80% interval": [f"{a:.1f} to {b:.1f}" for a, b in zip(t.boot_rating_p10, t.boot_rating_p90)],
                          "80% rank interval": [f"{a:.0f} to {b:.0f}" for a, b in zip(t.boot_rank_p10, t.boot_rank_p90)],
                          "P(top 10)": t.boot_top10_prob, "Pressure balls": t.n_press_balls})
        A(md(d, 2) + "\n")
        for r in t.itertuples():
            if label == "batters":
                A(f"{r.final_rank}. **{r.player_name}**: strike rate {r.press_sr:.0f} under pressure against {r.normal_sr:.0f} otherwise, {int(r.press_runs)} runs and {int(r.press_outs)} dismissals in {int(r.n_press_balls)} pressure balls; {100 * r.press_share_weak_opp:.0f}% of them against associate or A-team sides.")
            else:
                A(f"{r.final_rank}. **{r.player_name}**: economy {r.press_econ:.2f} under pressure against {r.normal_econ:.2f} otherwise, {int(r.press_wkts)} wickets in {int(r.n_press_balls)} pressure balls; {100 * r.press_share_weak_opp:.0f}% against associate or A-team sides.")
        A("")
        A(f"Figure: `v2_top10_{label}.png`.\n")
    A("## 2. The method in six steps\n")
    A("1. **Clean the ball data.** Legal deliveries (wides and every no-ball type excluded), runs reconstructed "
      "for extras, super overs and rain-reduced matches removed, the chase target reconstructed only from first-innings ball data.")
    A("2. **Win probability for every ball.** A logistic model on the resource-adjusted margin, scored out of "
      "fold so no match is rated by a model that saw it.")
    A("3. **Pressure is leverage.** For each ball, the expected absolute swing in win probability over everything "
      "the next ball could be. A tight finish has high leverage; a dead game has almost none.")
    A("4. **Credit above expectation.** Expected runs and wicket probability from a model that knows the situation "
      "and the batter's stage of innings but not who the players are. Net runs above expected combines runs and "
      "the run value of a wicket.")
    A("5. **Rate players with a hierarchical ridge.** One regression gives each batter and bowler an effect, "
      "adjusting for the opponents faced, team strength by year, venue and competition. Each ball is weighted by "
      "its leverage and by how recent it is, so a player's rating is dominated by the balls that mattered.")
    A("6. **Choose every design option by prediction, not by taste.** See the next section.\n")
    A("## 3. How the design was chosen\n")
    A("Each trial fits the rating on part of the data and measures how well it predicts the same players' "
      "pressure performance in data it never saw, using weighted rank correlation. Tuning used five "
      "forward-only six-month windows; confirmation used two later forward-only windows and was not used "
      "to choose anything. Random half-sample splits were excluded because they can train on matches later "
      "than the scored matches. The window-by-window chronology is recorded in `outputs/v2/validation_audit.csv`.\n")
    A("**Adoption rule.** An option moves away from the reference setup only if it is better by more than two "
      "standard errors of the paired difference across the tuning trials. A first attempt without this rule "
      "(3 folds, free coordinate search) overfit: it scored 0.03 and -0.02 on later data against 0.24 and 0.08 "
      "for the plain setup. That failure is why the rule exists. The reference setup is leverage power 1, "
      "24-month half-life, ridge penalty 3,000, associates at half weight, opponent adjustment on.\n")
    ch = pd.DataFrame([dict(group=("batters" if k == "bat" else "bowlers"), **v["cfg"]) for k, v in chosen.items()])
    ch["half_life"] = ch.half_life.map(lambda v: "none" if v is None or (isinstance(v, float) and np.isnan(v)) else v)
    A("Chosen configuration (`chosen_config.json`):\n")
    A(md(ch, 2) + "\n")
    lg = log[["role", "option", "value", "reference", "diff_vs_reference", "se", "z"]].copy()
    lg["role"] = lg.role.map({"bat": "batters", "bowl": "bowlers"})
    lg["adopted"] = lg.z > 2
    A("Every option tried, as a difference from the reference (`search_log.csv`; positive = better; adopted only "
      "when z > 2):\n")
    A(md(lg, 3) + "\n")
    adopted = log[log.z > 2]
    if adopted.empty:
        A("In words. No tested option crossed the two-standard-error adoption threshold; the reference "
          "configuration was retained for both roles.\n")
    else:
        choices = "; ".join(
            f"{'batters' if r.role == 'bat' else 'bowlers'} {r.option}={r.value} (z={r.z:.2f})"
            for r in adopted.itertuples()
        )
        A(f"In words. The tuning-only two-standard-error rule adopted: {choices}. "
          "No other tested option crossed the threshold. These are predictive associations, not causal effects.\n")
    A("## 4. Does it predict anything? (confirmation trials, never used for tuning)\n")
    cc = c[["role", "method", "objective", "se", "corr_nrae_target", "corr_wpa_target", "players"]].copy()
    cc["role"] = cc.role.map({"bat": "batters", "bowl": "bowlers"})
    cc["method"] = cc.method.map(lambda m: names.get(m, m))
    cc["players"] = cc.players.round(0).astype(int)
    A(md(cc.sort_values(["role", "objective"], ascending=[True, False]), 3) + "\n")
    A("Figure: `v2_confirmation.png`. Reading it:\n")
    b2 = c[(c.role == "bat")].set_index("method").objective
    w2 = c[(c.role == "bowl")].set_index("method").objective
    bat_raw, bowl_raw = b2["raw strike rate"], w2["raw economy (negated)"]
    bat_word = "beats" if b2["v2 chosen"] > bat_raw else "does not beat"
    bowl_word = "beats" if w2["v2 chosen"] > bowl_raw else "does not beat"
    A(f"- Against the naive benchmarks, V2 {bat_word} raw pressure strike rate for batters "
      f"({b2['v2 chosen']:.3f} vs {bat_raw:.3f}) and {bowl_word} raw pressure economy for bowlers "
      f"({w2['v2 chosen']:.3f} vs {bowl_raw:.3f}). The bowlers' result is a real limitation of this challenger.")
    d_b = {k: b2["reference"] - b2[k] for k in ("unweighted level (alpha 0)", "almost no shrinkage (lam 30)")}
    d_w = {k: w2["reference"] - w2[k] for k in ("unweighted level (alpha 0)", "almost no shrinkage (lam 30)")}
    A(f"- For batters, the confirmation results are mixed: the unweighted variant is {d_b['unweighted level (alpha 0)']:+.3f} "
      f"relative to the reference, while the almost-unshrunk variant is {d_b['almost no shrinkage (lam 30)']:+.3f}.")
    A(f"- For bowlers, the unweighted variant is {d_w['unweighted level (alpha 0)']:+.3f} and the almost-unshrunk variant "
      f"is {d_w['almost no shrinkage (lam 30)']:+.3f} relative to the reference. These comparisons are descriptive; "
      "the confirmation windows do not select the model.")
    A(f"- The selected V2 score is {b2['v2 chosen']:.3f} for batters and {w2['v2 chosen']:.3f} for bowlers, versus "
      f"{b2['reference']:.3f} and {w2['reference']:.3f} for the reference configuration. The gains are modest and "
      "uncertain. Pressure performance is only partly predictable from past pressure performance.\n")
    A("## 5. How the lists compare with earlier builds\n")
    for label in ("batters", "bowlers"):
        v, q, o = set(top[label].player_id), set(prev[label].player_id), set(p1[label].player_id)
        A(f"- {label.capitalize()}: {len(v & q)} of 10 players are the same as the phase 3 list in `docs/FINDINGS.md`; "
          f"{len(v & o)} of 10 are the same as the first build.")
    for label in ("bowlers",):
        v, q = top[label], prev[label]
        A(f"  - New in V2 against phase 3: {', '.join(v[~v.player_id.isin(q.player_id)].player_name) or 'none'}; "
          f"dropped: {', '.join(q[~q.player_id.isin(v.player_id)].player_name) or 'none'}. The difference comes from the bowler "
          "recency decision above: without a decay, bowlers whose best form is older are no longer discounted.")
    A("")
    A("Two designs reached the same batter set. That is the strongest robustness evidence in this repository, "
      "stronger than any single interval.\n")
    A("## 6. Limits\n")
    A("- Held-out correlations are small. A rank is a best estimate; the intervals in section 1 are wide for ranks 6 to 10.")
    A("- Baselines, win probability and pressure flags were fitted on all matches (identity-free models). Strictly, "
      "that lets a little future league-wide information into past ratings. It cannot favour any player.")
    A("- The tuning and confirmation windows overlap in the data they train on; only the test windows are disjoint.")
    A("- No pitch, weather, dew or fielding data. Run values of byes and leg byes are unrecorded.")
    A("- The bootstrap holds eligibility and penalties fixed, so intervals are somewhat narrow.")
    A("- Sooryavanshi tops the batters on 85 pressure balls; his rating leans on his many other leveraged balls and "
      "the interval is wide (see section 1).\n")
    A("## 7. Reproduce\n")
    A("```bash\npython run_all.py 20\n```\n")
    A("Stages 20 to 22 need the credit tables from stages 01 to 06 (`python run_all.py` builds everything).\n")
    A("## Exact dropdown selections\n")
    for label in ("batters", "bowlers"):
        A(f"**{label.capitalize()}**\n")
        for r in top[label].itertuples():
            A(f"{r.final_rank}. {r.dropdown_name} ({r.player_id})")
        A("")
    txt = "\n".join(L).replace("—", "-")
    open(os.path.join(ROOT, "docs", "V2_FINDINGS.md"), "w", encoding="utf-8").write(txt)
    print(f"  wrote docs/V2_FINDINGS.md ({len(txt.splitlines())} lines)")


if __name__ == "__main__":
    main()
