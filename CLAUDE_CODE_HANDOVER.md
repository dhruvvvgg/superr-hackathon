# SupeRR Selector Season 2: pressure-player model for Rajasthan Royals

This file is a self-contained build spec. Work autonomously from start to finish. Do not stop to ask questions. When something is ambiguous, pick the most defensible option, write the choice and the reason to `docs/DECISIONS.md`, and keep going.

## 1. Goal

Rajasthan Royals (RR) are running a hackathon called SupeRR Selector Season 2. The Round 1 task is to build a data-driven system that measures how batters and bowlers perform in high-pressure T20 situations compared with their usual level, then rank the players who deliver most consistently when it matters.

The final submission has two parts:

1. Two ordered top-10 lists, one for batters and one for bowlers, chosen from dropdowns on Unstop. Names must match the `player_name` values in `competition_team_player_mapping.csv`, and every list must match the report exactly.
2. A methodology report covering: how pressure was defined; the batting and bowling metrics, baselines and rating logic; fairness (sample size, eligibility, match context, IPL versus T20I); evidence for the top 10; reliability and limitations. A reader must be able to reproduce it.

The brief also says rankings must come from the supplied data, not reputation. The wider purpose is to tell RR which reliable-under-pressure players to back at the IPL 2027 auction, and how each could strengthen the squad. So you also produce an RR fit layer (section 9).

The evaluators will judge the rankings and the quality and transparency of the method. Aim for a result that is correct, stable under reasonable changes, honest about uncertainty, and easy to explain.

## 2. Working rules

- Never wait for input. Log every non-trivial decision, with the reason and the alternative you rejected, in `docs/DECISIONS.md`.
- Never leave the repo broken. Each commit must leave `python run_all.py` working or at least not worse than before.
- Commit often. Commit messages are plain descriptions of the change. Do not add AI attribution, session URLs, `Co-Authored-By` lines or tool signatures to any commit message. If an AI-use disclosure is required, put it in `README.md` only.
- Fix random seeds. Pin versions in `requirements.txt`. The whole pipeline must run from raw CSVs with one command.
- Raw files go in `data/raw/` and are never modified. Derived data goes in `data/interim/` and `data/processed/`.
- Pre-register the primary specification (section 6) in `docs/DECISIONS.md` and commit it before you look at any player ranking. You may fix bugs afterwards. You may not change the primary spec because a player you like or dislike ranks badly. Any change after seeing results must be logged as a post-hoc change with the evidence for it.
- No manual overrides of rankings. If a famous player is missing from the top 10, report his numbers and why, do not push him in.
- Use the tools you have. Web search is for the RR context in section 9 and for sanity checks only. If network access is blocked, say so in `docs/DECISIONS.md`, rely on `context/rr_auction_context.md`, and mark anything else as unverified.
- When finished, write `docs/FINDINGS.md` (structure in section 10). A second reviewer will read the repo and that file and build the submission document from them, so every number in FINDINGS must be traceable to a table or figure in `outputs/`.

## 3. Input files

Put the uploaded files in `data/raw/`. File names may carry a hash prefix; rename to the plain names below and note it in the README.

| file | contents |
|---|---|
| `ball_by_ball.csv` | 200,999 deliveries, 867 matches, 33 columns |
| `matches.csv` | 883 matches: comp_id, date, stage, venue, teams, toss, `revised_target`, `first_inn_revised_overs`, `second_inn_revised_overs`, `knock_out`, `win_team_id`, `result` |
| `competitions.csv` | comp_id, comp_name, match_format (T20 or T20I), season |
| `teams.csv` | comp_id to team_id and team_name |
| `playing_eleven.csv` | per match and team: player_id, batting_order, is_played, is_captain, is_wk, is_impact, is_impact_off |
| `competition_team_player_mapping.csv` | comp_id, team, player_id, player_name (1,217 player ids) |

Ball-by-ball columns: match_id, innings, overid, over_ball_num, innings_ball_num, batting_team_id, bowling_team_id, striker_id and name, non_striker_id and name, bowler_id and name, batting_type (RHB or LHB), bowling_type, batting_order, runs, is_four, is_six, is_wicket, dismissal_type_id, dismissal_type, dismissed_player_id, extras_type, extras1_runs, extras_2_runs, pace_or_spin, bowl_speed, stroke, delivery_style, over_or_around, on_or_off, delivery_ist_time.

## 4. Data facts already verified, and traps

These come from a profiling pass done before writing this spec. Re-verify each in `src/01_profile.py`, print the result, and record any difference in `docs/DECISIONS.md`.

Coverage
- 16 of the 883 matches have no ball-by-ball data. All 16 are "Match Abandoned".
- IPL 2022 to 2026 is present (371 matches listed, 367 with ball data; IPL 2024 has 3 missing). The rest is T20I plus two A-team T20 tournaments (comp_id 2670 Emerging Teams Asia Cup 2024, comp_id 3289 Asia Cup Rising Stars 2025, `match_format` = T20 but not IPL).
- Ball counts in innings 1 and 2: T20I about 106,300; IPL about 87,700; A-team about 7,000. Latest match date is 2026-11-01.
- Innings values 3 and 4 exist (38 balls total). They are super overs. Exclude them from the main analysis and log the count.

Run accounting, the biggest trap
- `runs` is runs off the bat only. On wides, byes and leg byes it is 0 (leg byes show a mean of about 0.0004). The run value of byes and leg byes is not stored anywhere.
- `extras1_runs` is a type code, not a run count: 1 = no-ball (`extras_type` "Overstep"), 2 = wide, 3 = leg bye, 4 = bye, 5 = "other", 6 = no extra, 7 = penalty (1 row). `extras_2_runs` is non-zero on only 36 rows (values 1 and 4).
- Reconstructing the real score therefore needs an assumption. Test on the 255 run-margin matches without a revised target: "each extra delivery adds 1 run plus `extras_2_runs`" reproduces the actual winning margin exactly in about 36% of matches, with a mean absolute error of about 2 runs. A least-squares fit of implied values gives wide about 1.2, no-ball about 1.2, leg bye about 1.35, bye about 2.2 (noisy), other about 1.4.
- Do this properly: fit per-type run values with a floor of 1 on those matches, report the exact-match rate and error, and use the fitted values for innings totals, targets and required run rate. Also validate on "Won by N wickets" matches: the chasing side's reconstructed total must reach the target and wickets lost must equal 10 minus N. The wicket check is exact and does not depend on extras, so treat it as the ground-truth test of your parsing.
- State plainly in the report that required-rate features carry a small reconstruction error of roughly 2 runs per innings.

Legal balls
- A legal delivery is any row whose `extras_type` is not "wide" and not "Overstep". "other" counts as legal. Verified: with this rule only 1 over has more than 6 legal balls, versus 244 if "other" is excluded.
- `over_ball_num` goes up to 13 because it counts illegal deliveries. Build your own legal-ball counter within each innings. `overid` runs 1 to 20.

Wickets
- `is_wicket` is true on 10,881 rows. Dismissal types: Caught, Bowled, LBW, RunOut, Stump, Hit Wicket, Retire Out, Obstructing the field (two spellings).
- `dismissed_player_id` equals the striker about 97.5% of the time. In the rest, the non-striker was dismissed (mostly run outs). One wicket row has a missing dismissed player. Charge the dismissal to `dismissed_player_id`.
- Bowler credit applies to Caught, Bowled, LBW, Stump and Hit Wicket only. Run outs, retired out and obstructing the field are not credited to the bowler. Retired out is tactical: exclude it from batter dismissal cost as well.

Reduced matches
- 23 matches carry a `revised_target` (rain or DLS). Exclude any match where `first_inn_revised_overs` or `second_inn_revised_overs` is set from the win-probability training set and from pressure analysis. Log the match count.

Identity
- `player_id` is consistent across IPL and T20I (for example Sanju Samson is 2258 in RR, CSK and India squads). Never join players by name. Seven names map to two ids each (Rashid Khan, Abdul Samad, Bashir Ahmad, Basil Hameed, Haider Ali, Mohammad Ali, Muhammad Farooq). Resolve by id, and in the final tables show the id next to the name so the Unstop dropdown pick is unambiguous.
- Team ids: RR is 3. Other IPL franchises are 1, 2, 4, 5, 7, 8, 242, 3508, 3509. RR's IPL 2026 squad is `comp_id` 3298, `team_id` 3 in the mapping file.
- `playing_eleven.batting_order` is empty for players who did not play. Use `is_played`.

Sample sizes
- Players with at least 200 balls faced: 217. With at least 500: 126. Players with at least 200 balls bowled: 232. With at least 500: 128.
- Opposition strength varies widely. The T20I data includes associates (Canada, Hong Kong, Japan, Kuwait, Nepal, Netherlands, Oman, Scotland, Singapore, UAE, USA) and weaker full members (Ireland, Zimbabwe). Treat opposition quality as a first-class adjustment, not an afterthought.

Other
- `bowl_speed` is zero on about 39% of rows and `stroke` is empty on about 3%. Do not rely on either as a core feature.

## 5. Repo layout

```
README.md                  how to run, data notes, AI disclosure if any
requirements.txt
run_all.py                 runs every stage in order
context/rr_auction_context.md   public context (supplied, see section 9)
data/raw/  data/interim/  data/processed/
src/01_profile.py          re-verify section 4, write outputs/tables/data_quality.csv
src/02_build_state.py      legal balls, extras calibration, match state, targets, features
src/03_win_prob.py         win-probability model (out-of-fold), calibration
src/04_pressure.py         leverage index, pressure tiers, validation tables and figures
src/05_expected.py         expected runs and expected wicket models, wicket value
src/06_attribution.py      ball-level credit for batters and bowlers (NRAE, WPA)
src/07_ratings.py          shrinkage, opponent adjustment, consistency, composite rating
src/08_robustness.py       bootstrap, sensitivity grid, persistence tests
src/09_rr_fit.py           RR gap and fit analysis
tests/                     pytest checks for the invariants in section 11
outputs/tables/ outputs/figures/
docs/DECISIONS.md  docs/FINDINGS.md
```

## 6. Primary specification (pre-register this)

### 6.1 Match state

For each delivery in innings 1 and 2 (non-reduced matches), build the state before the ball: legal balls bowled, balls left, score, wickets lost, current run rate; in innings 2 also target, runs needed, required run rate and the gap to current rate; plus runs and wickets in the last 12 balls and the current dot-ball streak. Add venue context (leave-one-match-out average first-innings score at the venue) and a competition tier (IPL, T20I, A-team).

### 6.2 Win probability

Fit a gradient-boosted classifier (LightGBM or similar) for "batting side wins" on the state features, separately or with an innings flag for innings 1 and 2. Use 5-fold cross-validation grouped by match, and use only the out-of-fold probabilities in everything downstream so no match is scored by a model that saw it. Do not include team identity in this model. Report log loss, Brier score and a calibration plot by innings. Drop matches with no winner. Handle ties by the final winner if `win_team_id` is set, otherwise drop and log.

### 6.3 Pressure definition

Pressure is how much the next ball can move the match.

- For each delivery compute the leverage index. Take the possible outcomes of the next ball (dot, 1, 2, 3, 4, 6, wicket, wide, no-ball), weight them by their empirical frequency for that phase (powerplay 1 to 6, middle 7 to 15, death 16 to 20) and innings, and average the absolute change in win probability each would cause. Divide by the global mean so a typical ball has leverage 1.
- Convert to a pressure score: the percentile of leverage within the innings (0 to 100).
- Tiers: Low below 50; Normal 50 to 80; High 80 to 95; Extreme 95 and above. The primary pressure sample is High and Extreme combined (score at or above 80).

Why this is meaningful: it combines required rate, wickets in hand, balls left, scoreline and contest closeness in one number learned from outcomes, instead of hand-picked cutoffs. It naturally ignores dead games (win probability near 0 or 1) and flags tight chases and late collapses.

Prove it separates pressure from ordinary play. In `src/04_pressure.py` produce, with phase, innings and wickets held fixed:
- strike rate, dot-ball %, boundary %, wicket rate and economy by tier, and the size of the shift from Normal to High;
- the composition of the High tier by innings, phase, wickets lost and required-rate band;
- a figure of average leverage by over for innings 1 and 2.
State honestly that part of any shift comes from selection (high-leverage states are where good teams are chasing), and show the within-phase and within-wickets comparison to limit that.

Also build rule-based alternatives for transparency and robustness, and report how strongly each correlates with the leverage-based flag:
- Variant B (contested-state rule): win probability between 0.25 and 0.75 and (balls left at most 48 or wickets lost at least 5).
- Variant C: leverage percentile at least 90.
- Variant D: leverage percentile at least 70.
- Variant E: death overs only (16 to 20) with win probability between 0.2 and 0.8.

### 6.4 Expected-value baselines (no player identity)

Fit out-of-fold models for expected runs off the bat per legal ball and for dismissal probability per legal ball. Features: phase, balls left, wickets lost, innings, required-rate gap, bowler pace or spin and bowling type, batter hand, venue, competition tier, free-hit or no-ball flag where inferable. Exclude batter and bowler ids so the baseline means "what an average player would do here".

Wicket value in runs: estimate a smoothed resource table of expected remaining runs by (balls left, wickets lost) from the data, and set the run value of a wicket at balls left b and wickets w to the drop in expected remaining runs from w to w+1.

### 6.5 Ball-level credit

- Batter net runs above expected: `NRAE_bat = (runs_off_bat - xRuns) - lambda * (dismissed - xWkt)`, only on legal balls faced (wides are not faced). Charge the dismissal to `dismissed_player_id`.
- Bowler net runs above expected, sign flipped so that higher is better: runs conceded include wides and no-ball runs using the calibrated extras values; wicket credit only for bowler-credited dismissals.
- Win probability added: change in out-of-fold win probability across the ball, credited to the striker (positive when the batting side gains) and to the bowler (negative of that).
- Because win probability swings scale with leverage, compare pressure with normal using NRAE, which is leverage-neutral. Use WPA as the impact measure inside the pressure sample.

### 6.6 Player estimates with opponent adjustment and shrinkage

Primary estimator: a crossed ridge regression on ball-level NRAE (sparse design matrix), with
- batter effect in normal situations;
- batter pressure delta (the extra effect when the ball is in the pressure sample);
- bowler effect;
- batting-team-by-season effect to absorb team strength;
- venue and competition tier as nuisance terms.
Choose the penalty by cross-validation grouped by match. The ridge penalty does the shrinkage and the bowler and team effects do the opponent adjustment together. Do the mirror model for bowlers. Batter pressure level = normal effect + pressure delta.

Cross-check estimator: empirical Bayes shrinkage of each player's raw pressure NRAE per 100 balls, with match-clustered standard errors and the prior variance estimated by method of moments or REML. Report the Spearman correlation between the two estimators. If it is below 0.8, investigate and explain.

Weights: recency weight with a 24-month half-life measured back from 2026-11-01. IPL and T20I full-member matches weight 1.0. A-team tournaments and T20I matches against associates weight 0.5. Keep the weights in a config file.

### 6.7 Consistency

Per player and per pressure innings (batters) or pressure spell (bowlers), compute whether NRAE was at or above 0. Shrink the hit rate with a beta-binomial prior fitted on the pool. Add a downside measure: the share of pressure innings or spells that were clearly bad (batter dismissed within 3 pressure balls for under 3 runs; bowler conceding more than 2 runs per ball above expected). Also compute the spread of per-innings NRAE (median absolute deviation).

### 6.8 Composite rating

For batters and bowlers separately, z-score each component among eligible players and combine:

```
Rating = 0.40 * Level      (opponent-adjusted, shrunk pressure NRAE per 100 balls)
       + 0.25 * Impact     (shrunk pressure WPA per 100 balls)
       + 0.20 * Consistency (shrunk hit rate, minus downside share)
       + 0.15 * Delta      (pressure level minus own normal level, shrunk)
```

Reasoning: RR wants players who deliver, so absolute performance under pressure carries the most weight; delta captures "compared with their usual level" from the brief but stays small so a weak player who is equally weak under pressure does not rank well. Flag any top-20 player whose delta is clearly negative as a "dips under pressure" case in FINDINGS.

### 6.9 Eligibility

Defaults, to be tested in the sensitivity grid at half and one-and-a-half times these values:
- Batters: at least 60 legal pressure balls faced and at least 12 pressure innings.
- Bowlers: at least 48 legal pressure balls bowled (8 overs) and at least 10 pressure spells.
- Both: at least 150 total balls in the dataset for a usable baseline, and at least one appearance in 2025 or 2026 (the auction cares about current players).
- If fewer than 40 players qualify in either group, lower the thresholds and log it. Report the split-half reliability at the chosen thresholds.

## 7. Uncertainty and robustness (must do)

1. Cluster bootstrap by match, at least 1,000 resamples, re-running the full rating. Report for each top-20 player: mean rank, 80% rank interval, and the probability of finishing in the top 10.
2. Sensitivity grid: pressure variants A (primary), B, C, D, E; weight perturbations (draw 200 weight vectors from a Dirichlet centred on the primary weights); eligibility thresholds at three levels; recency on and off; IPL-only, T20I-only, and with or without A-team and associate matches; ridge estimator versus empirical Bayes. Produce a matrix of top-10 membership frequency per player.
3. Persistence test: split matches by season (2022 to 2024 versus 2025 to 2026) and by odd and even match, compute the rating in each half, and report the rank correlation across halves. This shows whether the metric measures a repeatable skill or noise. If persistence is weak, say so in the report and do not oversell.
4. Decision rule fixed in advance: the final order is the primary composite. If a player in the primary top 10 has a top-10 probability across the sensitivity grid below 0.40, replace him with the best-ranked outsider whose probability is at least 0.40, and log the swap. Otherwise keep the primary list.
5. Face-validity audit (no overrides): list the 15 most-capped death-over batters and bowlers by volume and show where each sits and why. Check the top 10s are not dominated by players whose pressure numbers come mostly from associate-nation opposition.

## 8. Required tables and figures

Tables (CSV, in `outputs/tables/`): `data_quality.csv`, `extras_calibration.csv`, `wp_model_metrics.csv`, `pressure_validation.csv`, `batter_ratings.csv`, `bowler_ratings.csv` (all eligible players with components, shrunk estimates, ranks, intervals, top-10 probability), `top10_batters.csv`, `top10_bowlers.csv` (with ids and exact dropdown names), `sensitivity_membership.csv`, `persistence.csv`, `rr_fit.csv`.

Figures (PNG, readable at slide size, light background, labelled axes): win-probability calibration; leverage by over; strike rate, dot% and wicket rate by tier; pressure sample composition; top-10 rating bars with 80% intervals for each group; top-10 membership heatmap across the sensitivity grid; persistence scatter; pressure level versus normal level scatter for the top 20 (shows who dips and who lifts); RR gap chart.

## 9. RR fit layer for the IPL 2027 auction

Public context is in `context/rr_auction_context.md` (supplied alongside this file). Use it, and use web search to extend it if you have network access. Mark each fact as sourced or unverified. Do not invent squad facts.

Build `outputs/tables/rr_fit.csv` and a section in FINDINGS covering:

1. RR's own pressure profile from the data: team-level pressure NRAE by phase for batting and bowling, 2025 and 2026 IPL, split by chasing and setting. Identify where RR lose or gain under pressure. Use `comp_id` 3298 team 3 for the 2026 squad and the matching IPL 2025 comp for 2025.
2. For each top-10 player: role and usage (batting position and phase mix; bowling phase mix, pace or spin, type), handedness, pressure performance against pace and against spin (batters) or against left- and right-handers (bowlers), trend between 2022 to 2024 and 2025 to 2026, IPL versus T20I split, IPL 2026 franchise, and national team (use to flag likely overseas status; overseas status is not a column in the data, so mark it as derived).
3. Gap analysis: which RR incumbents in the same role he would compete with, and the pressure-rating difference between him and the weakest regular in that role. Say "would displace" only where the numbers support it.
4. Availability: whether the player is likely in the auction pool. Retention lists are not out as of this writing, so keep an `availability` column set to "unknown, check after retention list" unless you can verify it from a primary source.
5. Squad-rule constraints that shape the picks: squad size limits and the overseas limits, stated as known IPL rules and flagged as to-verify if you cannot source them.

Keep the two outputs separate. The Unstop top-10 lists are pure pressure-performance rankings from the data. The RR layer adds availability and fit commentary on top, and may add a shorter auction shortlist that draws from the top 20 of each group.

## 10. Final deliverable: `docs/FINDINGS.md`

Write it so a reviewer who has not seen the work can build the submission from it. Sections:

1. Result in one page: the two top-10 lists with ratings, 80% intervals and top-10 probabilities, plus a one-line reason for each player.
2. Pressure definition and validation, with the key numbers.
3. Data quality log, including extras calibration accuracy and the wicket check result.
4. Win-probability model performance.
5. Metrics, baselines and rating logic with the final weights.
6. Fairness choices: eligibility thresholds, recency, opposition adjustment, IPL versus T20I, A-team and associate handling.
7. Evidence for the top 10: tables and figure references.
8. Robustness and persistence results, including any swaps made by the decision rule.
9. RR fit layer.
10. Limitations and where the model is least certain: extras reconstruction error, small pressure samples, selection effects in high-leverage states, team context, role differences, no pitch or weather data, and anything else you found.
11. Honest weak spots: cases where results undercut a simple story. Do not soften them.
12. Reproduction steps and runtime.
13. Open questions and anything you would do with more time.

Add a final block listing the exact dropdown selections, rank 1 to 10 for each group, as `player_name (player_id)`.

## 11. Tests and acceptance checks

The pipeline is done only when all of these pass and are shown in `outputs/tables/data_quality.csv` or the test output:

- Legal-ball counter gives 6 legal balls in nearly every full over, and 120 legal balls in complete 20-over innings.
- Reconstructed wickets lost at the end of each chase match the "Won by N wickets" result.
- Extras calibration error is reported and is no worse than the simple 1-run assumption.
- Out-of-fold win probability is calibrated: reliability bins within 0.03 of the diagonal where data is dense, and log loss beats a state-free baseline.
- No player appears twice in a list. Every listed name exists in the mapping file and every id resolves to exactly one name.
- Re-running `python run_all.py` from scratch reproduces the same top-10 lists.
- No em dashes or AI attribution in README, commit messages or FINDINGS.

## 12. Order of work

1. Profile and verify (01). Write the pre-registration into DECISIONS.md and commit.
2. State, extras calibration, win probability (02, 03). Check calibration before moving on.
3. Pressure definition and validation (04). Confirm the tier shifts are real before moving on.
4. Baselines, attribution, ratings (05 to 07).
5. Robustness and persistence (08).
6. RR layer (09).
7. FINDINGS.md, README, tests, final clean run from scratch.

Take your time and be meticulous. A correct, stable and well-explained result matters more than a complicated model.
