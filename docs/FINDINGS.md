# FINDINGS: who delivers under pressure

Every number below is read from a file in `outputs/tables/` when the pipeline runs (`src/11_report.py`). The file is named next to each table. Figures are in `outputs/figures/`.

## 1. Result in one page

Rating is the composite pressure rating. The interval is the 80% interval from a match bootstrap (1000 resamples). P(top 10) boot is the share of bootstrap resamples in which the player finishes in the top 10. P(top 10) grid is the share of sensitivity-grid configurations in which he does.

### Top 10 batters (`top10_batters.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) boot | P(top 10) grid | Pressure balls |
|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi (50284) | 2.68 | 0.97 to 3.04 | 1 to 14 | 0.88 | 0.50 | 85 |
| 2 | Abhishek Sharma (6281) | 2.25 | 0.52 to 2.66 | 1 to 32 | 0.72 | 0.69 | 300 |
| 3 | Tim David (6396) | 2.01 | 0.77 to 2.19 | 2 to 21 | 0.75 | 0.85 | 321 |
| 4 | Namboori Tilak Varma (7897) | 2.00 | 0.72 to 2.21 | 1 to 22 | 0.71 | 0.92 | 514 |
| 5 | Phil Salt (5553) | 1.70 | 0.62 to 1.81 | 3 to 28 | 0.62 | 0.78 | 200 |
| 6 | Heinrich Klaasen (4260) | 1.53 | 0.42 to 1.68 | 3 to 39 | 0.46 | 0.77 | 256 |
| 7 | Sahibzada Farhan (3091) | 1.41 | 0.29 to 1.67 | 4 to 48 | 0.43 | 0.46 | 128 |
| 8 | Pathum Nissanka (6931) | 1.35 | 0.14 to 1.73 | 3 to 60 | 0.42 | 0.59 | 263 |
| 9 | Shreyas Iyer (3647) | 1.33 | 0.09 to 1.67 | 3 to 65 | 0.35 | 0.54 | 293 |
| 10 | Fakhar Zaman (2921) | 1.28 | 0.13 to 1.24 | 8 to 61 | 0.16 | 0.42 | 185 |

1. **Vaibhav Sooryavanshi**: Leads on pressure level (+4.6) and lift over own normal level (+2.1); strike rate 238 under pressure against 220 otherwise, 202 runs and 4 dismissals in 85 pressure balls.
2. **Abhishek Sharma**: Leads on pressure level (+4.2) and lift over own normal level (+1.9); strike rate 202 under pressure against 185 otherwise, 606 runs and 18 dismissals in 300 pressure balls.
3. **Tim David**: Leads on pressure level (+2.9) and consistency (+1.9); strike rate 192 under pressure against 172 otherwise, 615 runs and 23 dismissals in 321 pressure balls.
4. **Namboori Tilak Varma**: Leads on lift over own normal level (+4.8) and win-probability impact (+2.4); strike rate 167 under pressure against 137 otherwise, 856 runs and 20 dismissals in 514 pressure balls.
5. **Phil Salt**: Leads on pressure level (+2.3) and consistency (+2.1); strike rate 170 under pressure against 171 otherwise, 340 runs and 7 dismissals in 200 pressure balls.
6. **Heinrich Klaasen**: Leads on pressure level (+2.0) and lift over own normal level (+1.4); strike rate 184 under pressure against 163 otherwise, 470 runs and 14 dismissals in 256 pressure balls.
7. **Sahibzada Farhan**: Leads on win-probability impact (+1.5) and lift over own normal level (+1.4); strike rate 165 under pressure against 132 otherwise, 211 runs and 7 dismissals in 128 pressure balls.
8. **Pathum Nissanka**: Leads on lift over own normal level (+1.7) and consistency (+1.6); strike rate 153 under pressure against 133 otherwise, 403 runs and 13 dismissals in 263 pressure balls.
9. **Shreyas Iyer**: Leads on win-probability impact (+2.2) and lift over own normal level (+1.7); strike rate 155 under pressure against 154 otherwise, 454 runs and 12 dismissals in 293 pressure balls.
10. **Fakhar Zaman**: Leads on consistency (+2.5) and lift over own normal level (+2.1); strike rate 171 under pressure against 121 otherwise, 316 runs and 7 dismissals in 185 pressure balls.

### Top 10 bowlers (`top10_bowlers.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) boot | P(top 10) grid | Pressure balls |
|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah (2933) | 3.19 | 1.59 to 3.01 | 1 to 5 | 0.97 | 1.00 | 366 |
| 2 | Varun Chakravarthy (6256) | 2.62 | 1.25 to 2.49 | 1 to 10 | 0.91 | 1.00 | 401 |
| 3 | Sunil Narine (781) | 2.21 | 0.98 to 2.11 | 2 to 16 | 0.80 | 0.92 | 351 |
| 4 | Rashid Khan (4722) | 2.10 | 0.68 to 2.26 | 2 to 29 | 0.68 | 0.83 | 484 |
| 5 | Bhuvneshwar Kumar (360) | 1.82 | 0.49 to 2.33 | 2 to 39 | 0.62 | 0.82 | 560 |
| 6 | Axar Patel (2876) | 1.73 | 0.46 to 1.94 | 3 to 41 | 0.48 | 0.64 | 446 |
| 7 | Mohsin Khan (6669) | 1.46 | 0.29 to 2.08 | 2 to 55 | 0.44 | 0.67 | 151 |
| 8 | Nathan Ellis (7920) | 1.35 | 0.35 to 1.68 | 4 to 49 | 0.35 | 0.75 | 247 |
| 9 | Josh Hazlewood (830) | 1.34 | 0.23 to 1.80 | 4 to 59 | 0.37 | 0.65 | 333 |
| 10 | Jason Holder (2633) | 1.15 | 0.24 to 1.53 | 6 to 59 | 0.26 | 0.31 | 422 |

1. **Jasprit Bumrah**: Leads on pressure level (+3.9) and lift over own normal level (+3.2); economy 7.07 under pressure against 7.15 otherwise, 20 wickets in 366 pressure balls.
2. **Varun Chakravarthy**: Leads on consistency (+4.0) and pressure level (+2.5); economy 7.59 under pressure against 8.16 otherwise, 25 wickets in 401 pressure balls.
3. **Sunil Narine**: Leads on pressure level (+2.5) and win-probability impact (+2.3); economy 6.74 under pressure against 6.80 otherwise, 14 wickets in 351 pressure balls.
4. **Rashid Khan**: Leads on lift over own normal level (+2.7) and win-probability impact (+2.1); economy 7.40 under pressure against 7.40 otherwise, 41 wickets in 484 pressure balls.
5. **Bhuvneshwar Kumar**: Leads on pressure level (+2.6) and lift over own normal level (+2.3); economy 8.87 under pressure against 8.04 otherwise, 39 wickets in 560 pressure balls.
6. **Axar Patel**: Leads on lift over own normal level (+4.4) and consistency (+2.2); economy 7.38 under pressure against 7.97 otherwise, 24 wickets in 446 pressure balls.
7. **Mohsin Khan**: Leads on lift over own normal level (+2.2) and pressure level (+1.7); economy 8.41 under pressure against 8.51 otherwise, 11 wickets in 151 pressure balls.
8. **Nathan Ellis**: Leads on pressure level (+1.7) and lift over own normal level (+1.6); economy 8.49 under pressure against 8.06 otherwise, 16 wickets in 247 pressure balls.
9. **Josh Hazlewood**: Leads on pressure level (+2.2) and win-probability impact (+1.6); economy 8.17 under pressure against 8.29 otherwise, 24 wickets in 333 pressure balls.
10. **Jason Holder**: Leads on pressure level (+2.2) and consistency (+1.1); economy 9.60 under pressure against 8.79 otherwise, 24 wickets in 422 pressure balls.

The bootstrap interval of a top-ranked player usually sits below his point rating. That is expected: the players at the top of a noisy ranking are partly there by luck, and resampling the matches pulls them back. Read the interval as the honest range.

## 2. Pressure definition and validation

**Definition.** Pressure is how much the next ball can move the match. For every delivery the out-of-fold win-probability model scores the state after each possible next-ball outcome (dot, 1, 2, 3, 4, 6, wicket, wide, no-ball). Leverage is the expected absolute change in win probability, weighting outcomes by their frequency in that phase and innings, divided by the global mean so an average ball has leverage 1. The pressure score is the percentile of leverage among all deliveries of the same innings number. Tiers: Low below 50, Normal 50 to 80, High 80 to 95, Extreme above. The pressure sample is score at or above 80.

**Why it is meaningful.** One number learned from match outcomes combines required rate, wickets in hand, balls left and closeness. A dead game has win probability near 0 or 1, nothing the next ball does can move it, and leverage is low without any hand-set cutoff.

**Does leverage measure what it claims?** Leverage is computed before the ball; the realised absolute win-probability change is observed after. Their Spearman correlation is 0.57. The top 20% of deliveries by leverage move win probability by 3.8 points on average, the bottom 50% by 0.9 points (`leverage_validity.csv`).

Outcomes by tier (`pressure_validation.csv`, table = tier overall; figure `pressure_tier_metrics.png`):

| tier | deliveries | strike_rate | dot_pct | boundary_pct | wickets per 100 balls | economy | mean_leverage | mean abs WP change (pts) |
|---|---|---|---|---|---|---|---|---|
| Low | 96667 | 137.60 | 36.96 | 18.07 | 5.42 | 8.58 | 0.52 | 0.93 |
| Normal | 58000 | 139.28 | 37.36 | 19.01 | 5.28 | 8.67 | 1.14 | 2.03 |
| High | 29001 | 142.42 | 37.00 | 19.45 | 5.73 | 8.88 | 1.65 | 2.91 |
| Extreme | 9668 | 147.91 | 36.28 | 19.73 | 8.20 | 9.29 | 3.05 | 5.50 |

Shift from the Normal tier to the pressure sample (`pressure_validation.csv`, table = shift):

| metric | raw shift Normal to Pressure | shift with innings, phase and wickets band held fixed | cells_used | cells_same_sign |
|---|---|---|---|---|
| strike_rate | 4.51 | 0.41 | 13 | 6 |
| dot_pct | -0.54 | 1.19 | 13 | 9 |
| boundary_pct | 0.51 | 0.36 | 13 | 6 |
| wicket_pct | 1.07 | 0.24 | 13 | 7 |
| economy | 0.32 | 0.02 | 13 | 6 |

Read this honestly. The tiers separate the stakes very clearly (the win-probability column). The behavioural shift is real in the raw numbers but most of it is composition: pressure balls sit more in the death overs and in tight chases, where everyone scores faster and gets out more. With innings, phase and wickets held fixed the shift is small. So pressure, as defined here, marks the balls that decide matches; it does not by itself make the average player bat or bowl very differently. Part of what remains is selection: high-leverage states are reached more often by good teams in close games.

Composition of the pressure sample (`pressure_composition.csv`, figure `pressure_composition.png`): innings 1 52% and innings 2 48% by construction; powerplay 30%, middle 32%, death 37% (death overs are 23% of all deliveries); 92% of pressure balls have win probability between 0.2 and 0.8 and 0.1% are in decided games. Average leverage by over is in `leverage_by_over.png`: it rises through the death overs and peaks in the last over of a chase.

Rule-based alternatives and their agreement with the primary flag (`pressure_variants.csv`):

| variant | definition | share_of_deliveries | phi_with_A | jaccard_with_A | share_innings1 |
|---|---|---|---|---|---|
| A | primary: leverage percentile >= 80 within innings number | 0.20 | 1.00 | 1.00 | 0.52 |
| B | WP in 0.25-0.75 and (balls left <= 48 or wickets lost >= 5) | 0.19 | 0.26 | 0.26 | 0.81 |
| C | leverage percentile >= 90 | 0.10 | 0.67 | 0.50 | 0.52 |
| D | leverage percentile >= 70 | 0.30 | 0.76 | 0.67 | 0.52 |
| E | overs 16-20 and WP in 0.2-0.8 | 0.13 | 0.28 | 0.24 | 0.82 |
| F | leverage percentile >= 80, global (both innings pooled) | 0.20 | 0.53 | 0.45 | 0.15 |

## 3. Data quality log

`src/01_profile.py` re-verified 48 facts from the build specification (`data_quality.csv`). Differences:

| check | claimed | observed | note |
|---|---|---|---|
| overs with >6 legal balls, other legal (handover rule) | 1 if other is legal, 244 if excluded | 244 | innings with >120 legal balls: 150; innings with exactly 120: 873 |
| DLS in result text but no revised field | 0 | 4 | also excluded as reduced |
| batters with >=200 balls faced | 217 | 214 |  |
| batters with >=500 balls faced | 126 | 122 |  |
| bowlers with >=200 balls bowled | 232 | 226 |  |
| bowlers with >=500 balls bowled | 128 | 123 |  |

- **Legal balls.** The specification's rule ("other" extras are legal) gives 244 overs with more than six legal balls. Treating "other" as a no-ball gives 1. The adopted rule is: illegal = wide, Overstep, other.
- **Wicket check.** 419/419 matches; one result string corrected from an outside source (D-24) agree with the result string. One result string was wrong: match 20190 (LSG v SRH, 7 April 2023) says 6 wickets, while the ball data and five outside scorecards show LSG won by 5 wickets with 127/5. It is corrected by a documented override in `config.json` (DECISIONS.md, D-24). This check does not depend on extras.
- **Extras calibration** (`extras_calibration.csv`). Fitted run values: wide 1.08, no-ball 1.00, other no-ball 1.00, leg bye 1.08, bye 1.69. On 396 clean run-margin matches the mean absolute error of the reconstructed margin is 2.14 runs (1-run rule 2.17; out of sample 2.17). The margin is exact in 32% of matches with the 1-run rule and within 2 runs in 57% with the fitted values. The fitted values barely beat the 1-run rule: the residual error is not about the average value of an extra, it is unrecorded bye and leg-bye runs and occasional missing deliveries.
- **Why the target is anchored to the result.** In 42% of chases won by wickets the reconstructed chasing total is still below the reconstructed target at the end. The chase target is therefore recovered from the result string (DECISIONS.md, D-07). Required-rate features early in a chase still carry the reconstruction error of roughly 2 runs per innings.
- **Exclusions.** no ball data: 16; reduced (revised fields or DLS text): 38; no winner (no result / abandoned) with balls, not reduced: 14; first innings incomplete without flag: 5; second innings unresolved or result inconsistent: 1. Clean matches kept: 809. Super-over deliveries dropped: 38.
- **Scorecard audit** (`audit_scorecards.csv`). Ten seeded random matches were rebuilt from the ball data: winner and wickets agree with the result string in 10 of 10; run-margin errors range from 0.5 to 4.7 runs.
- **Integrity audit** (`audit_integrity.csv`). 15 checks pass and 0 fail: no duplicated deliveries, no super-over or reduced-match deliveries downstream, no wide counted as a ball faced, no run out credited to a bowler, no match scored by a model that saw it, one name per player id.

## 4. Win-probability model

Primary model: one logistic regression per innings on a degree-2 polynomial of the resource-adjusted margin, balls left, wickets lost and the three momentum features. The margin is (expected remaining runs minus runs needed) in a chase and (projected total minus venue average) when setting, scaled by the square root of balls left. Expected remaining runs come from a resource table fitted inside each training fold. Five folds grouped by match; only out-of-fold predictions are used downstream. No team or player identity.

`wp_model_metrics.csv` (out-of-fold; lower is better):

| model | role | description | log_loss | log_loss_inn1 | log_loss_inn2 | brier | max_calib_gap_dense_bins |
|---|---|---|---|---|---|---|---|
| respoly_mom | primary | respoly plus momentum features (last 12 balls, dot streak) | 0.5220 | 0.6364 | 0.3976 | 0.1781 | 0.0259 |
| respoly | comparison | logistic, degree-2 polynomial of resource margin z, balls left, wickets | 0.5221 | 0.6361 | 0.3981 | 0.1781 | 0.0356 |
| resz | comparison | logistic on resource margin z only | 0.5242 | 0.6358 | 0.4028 | 0.1784 | 0.0327 |
| mono | comparison | LightGBM, monotone constraints, raw state (originally pre-registered) | 0.5327 | 0.6396 | 0.4164 | 0.1810 | 0.0327 |
| free | comparison | LightGBM, unconstrained, innings flag, raw state | 0.5337 | 0.6405 | 0.4175 | 0.1816 | 0.0311 |
| logit | comparison | additive spline logistic regression on raw state | 0.5263 | 0.6393 | 0.4034 | 0.1793 | 0.0376 |
| base_rate | baseline | state-free baseline (win rate of the batting side by innings) | 0.6937 | 0.6942 | 0.6931 | 0.2503 | 0.0438 |

Calibration (`wp_calibration_bins.csv`, figure `wp_calibration.png`): the largest gap between predicted and observed win rate in bins with at least 5,000 deliveries is 0.026, and 20 of 20 bins lie within two standard deviations of match-bootstrap noise. First-innings win probability is close to a coin flip by nature (log loss near 0.64); most of the model's information is in the chase.

## 5. Metrics, baselines and rating logic

**Units.** A batter's unit is a ball faced (any delivery that is not a wide). A bowler's unit is a legal-ball slot: one legal ball plus the wides and no-balls that preceded it.

**Baselines without player identity** (`expected_model_metrics.csv`). Out-of-fold LightGBM models give expected bat runs and dismissal probability per ball faced, and expected runs charged and wicket probability per bowler slot. Features: innings, phase, balls left, wickets lost, current and required rate and their gap, venue average, competition tier, pace or spin, bowling type, batter hand, no-ball and free-hit flags, plus balls already faced by the striker in the innings and his batting position (the role-aware baseline adopted in phase 2).

| model | n | metric | oof | phase_mean_baseline | mean_actual | mean_pred |
|---|---|---|---|---|---|---|
| batter xRuns | 185928 | RMSE | 1.7107 | 1.7381 | 1.3934 | 1.3936 |
| batter xWkt | 185928 | log loss | 0.2075 | 0.2088 | 0.0542 | 0.0557 |
| bowler xRuns | 185122 | RMSE | 1.7459 | 1.7739 | 1.4473 | 1.4472 |
| bowler xWkt | 185122 | log loss | 0.2046 | 0.2054 | 0.0529 | 0.0543 |

**Wicket value in runs** (`resource_table.csv`). Expected remaining first-innings runs are fitted as R_w(b) = a_w (1 - exp(-b / t_w)) with a non-crossing penalty. The value of a wicket is the drop in expected remaining runs from w to w+1 wickets down. Examples: 120 balls left, 0 down: 12.4 runs; 60 balls left, 0 down: 2.2 runs; 24 balls left, 0 down: 0.0 runs; 120 balls left, 3 down: 12.6 runs; 60 balls left, 3 down: 7.7 runs; 24 balls left, 3 down: 3.3 runs; 120 balls left, 6 down: 17.1 runs; 60 balls left, 6 down: 13.3 runs; 24 balls left, 6 down: 6.1 runs.

**Ball-level credit.**

- Batter NRAE (net runs above expected) = (bat runs - expected runs) - wicket value x (dismissed - expected dismissal). The dismissal is charged to the dismissed player; non-striker run outs and dismissals off wides are dismissal-only records. Retired out costs nothing.
- Bowler NRAE = (expected runs - runs charged) + wicket value x (bowler wicket - expected wicket). Wides and no-balls are charged, byes and leg byes are not. Run outs and retirements are not credited.
- WPA = change in out-of-fold win probability across the ball, to the striker and with opposite sign to the bowler.

**Player estimates.** A weighted crossed ridge regression on ball-level NRAE with: player normal effect, player pressure delta, opponent effect (bowler for batters, striker for bowlers), own-team-by-season effect, venue, tier and an unpenalised pressure indicator. Penalties chosen by 5-fold cross-validation grouped by match (`ridge_cv.csv`): batters main 1000, delta 30000; bowlers main 1000, delta 30000. The cross-validated error surface is almost flat in the delta penalty and for bowlers the choice sits at the largest value in the grid: the data contain very little information about individual pressure deltas.

**Four components per player.**

| Component | Weight | Definition |
|---|---|---|
| Level | 0.40 | ridge normal effect + pressure delta, NRAE per 100 balls, opponent-adjusted and shrunk |
| Impact | 0.25 | pressure WPA per 100 balls, empirical Bayes shrinkage with match-clustered errors |
| Consistency | 0.20 | share of pressure innings or spells with NRAE at or above 0, minus the share that were clearly bad, both beta-binomial shrunk |
| Delta | 0.15 | ridge pressure delta: pressure level minus own normal level |

Each component is z-scored among eligible players and the rating is the weighted sum.

**Cross-check estimator** (`estimator_agreement.csv`). Empirical Bayes shrinkage of raw pressure NRAE:

| role | quantity | n | value |
|---|---|---|---|
| bat | level: ridge vs empirical Bayes | 153 | 0.36 |
| bat | delta: ridge vs empirical Bayes | 153 | 0.84 |
| bat | composite rating: ridge vs empirical Bayes | 153 | 0.80 |
| bat | top-10 overlap: ridge vs empirical Bayes | 10 | 0.50 |
| bowl | level: ridge vs empirical Bayes | 166 | 0.46 |
| bowl | delta: ridge vs empirical Bayes | 166 | 0.88 |
| bowl | composite rating: ridge vs empirical Bayes | 166 | 0.83 |
| bowl | top-10 overlap: ridge vs empirical Bayes | 10 | 0.50 |

The Level correlation is below the 0.8 the specification asked us to investigate. The cause is structural, not a bug: the ridge Level is normal effect plus delta and borrows strength from all of a player's balls, while the empirical Bayes Level uses pressure balls only, about a fifth of the sample. The two answer slightly different questions and the second is much noisier.

## 6. Fairness choices

- **Eligibility.** Batters: at least 60 pressure balls faced and 12 pressure innings. Bowlers: at least 48 pressure balls and 10 pressure spells. Both: at least 150 balls in total and an appearance in 2025 or 2026. 153 batters and 166 bowlers qualify, so no threshold was lowered.
- **Sample size.** Shrinkage (ridge, empirical Bayes, beta-binomial) pulls small samples toward the pool mean, so a short hot streak cannot top the list on its own.
- **Recency.** Weights halve every 24 months back from 2026-11-01.
- **Opposition.** The ridge estimates each player against the specific opponents he met and absorbs team strength by season. Deliveries against associate-nation opposition and all A-team tournament deliveries weigh 0.5. An associate player facing a full member keeps full weight.
- **IPL versus T20I.** Both are pooled with a tier term in every model. IPL-only and T20I-only ratings are run as sensitivity configurations (section 8).
- **Weak-opposition check.** Largest share of pressure balls against associate or A-team opposition among the top-10 batters: 13%; among the top-10 bowlers: 5% (`top10_batters.csv`, `top10_bowlers.csv`).

## 7. Evidence for the top 10

**Batters** (`top10_batters.csv`; all eligible players in `batter_ratings.csv`):

| final_rank | player_name | z_level | z_impact | z_consistency | z_delta | level | normal | delta | n_press_balls | n_press_innings | press_sr | normal_sr | press_avg | press_share_ipl | ipl_2026_team | national_team |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | 4.56 | 0.86 | 1.67 | 2.09 | 19.48 | 19.34 | 0.14 | 85 | 19 | 237.65 | 219.76 | 50.50 | 0.69 | Rajasthan Royals | India |
| 2 | Abhishek Sharma | 4.17 | 0.41 | 0.98 | 1.93 | 17.95 | 17.82 | 0.13 | 300 | 75 | 202.00 | 185.38 | 33.67 | 0.67 | Sunrisers Hyderabad | India |
| 3 | Tim David | 2.88 | 1.05 | 1.86 | 1.52 | 12.86 | 12.76 | 0.10 | 321 | 56 | 191.59 | 171.95 | 26.74 | 0.60 | Royal Challengers Bengaluru | Australia |
| 4 | Namboori Tilak Varma | 0.82 | 2.40 | 1.73 | 4.80 | 4.72 | 4.41 | 0.30 | 514 | 79 | 166.54 | 137.04 | 42.80 | 0.57 | Mumbai Indians | India |
| 5 | Phil Salt | 2.31 | 0.51 | 2.15 | 1.43 | 10.61 | 10.51 | 0.10 | 200 | 41 | 170.00 | 171.12 | 48.57 | 0.41 | Royal Challengers Bengaluru | England |
| 6 | Heinrich Klaasen | 1.97 | 1.06 | 1.34 | 1.42 | 9.26 | 9.16 | 0.10 | 256 | 48 | 183.59 | 163.34 | 33.57 | 0.87 | Sunrisers Hyderabad | South Africa |
| 7 | Sahibzada Farhan | 1.39 | 1.50 | 1.34 | 1.39 | 6.95 | 6.86 | 0.10 | 128 | 25 | 164.84 | 132.15 | 30.14 | 0.00 |  | Pakistan |
| 8 | Pathum Nissanka | 1.52 | 0.65 | 1.59 | 1.73 | 7.48 | 7.37 | 0.12 | 263 | 46 | 153.23 | 133.10 | 31.00 | 0.23 | Delhi Capitals | Sri Lanka |
| 9 | Shreyas Iyer | 0.50 | 2.17 | 1.67 | 1.70 | 3.45 | 3.33 | 0.11 | 293 | 52 | 154.95 | 154.48 | 37.83 | 0.68 | Punjab Kings | India |
| 10 | Fakhar Zaman | -0.10 | 2.01 | 2.53 | 2.10 | 1.07 | 0.93 | 0.14 | 185 | 34 | 170.81 | 120.65 | 45.14 | 0.00 |  | Pakistan |

**Bowlers** (`top10_bowlers.csv`; all eligible players in `bowler_ratings.csv`):

| final_rank | player_name | z_level | z_impact | z_consistency | z_delta | level | normal | delta | n_press_balls | n_press_innings | press_econ | normal_econ | press_wkts | press_share_ipl | ipl_2026_team | national_team |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah | 3.88 | 2.41 | 2.75 | 3.23 | 15.78 | 15.59 | 0.18 | 366 | 56 | 7.07 | 7.15 | 20 | 0.77 | Mumbai Indians | India |
| 2 | Varun Chakravarthy | 2.52 | 2.08 | 3.97 | 1.98 | 10.50 | 10.39 | 0.11 | 401 | 64 | 7.59 | 8.16 | 25 | 0.74 | Kolkata Knight Riders | India |
| 3 | Sunil Narine | 2.49 | 2.27 | 2.24 | 1.30 | 10.39 | 10.32 | 0.08 | 351 | 54 | 6.74 | 6.80 | 14 | 1.00 | Kolkata Knight Riders |  |
| 4 | Rashid Khan | 1.91 | 2.08 | 2.02 | 2.71 | 8.15 | 7.99 | 0.16 | 484 | 80 | 7.40 | 7.40 | 41 | 0.69 | Gujarat Titans | Afghanistan |
| 5 | Bhuvneshwar Kumar | 2.62 | 0.84 | 1.13 | 2.27 | 10.89 | 10.76 | 0.13 | 560 | 78 | 8.87 | 8.04 | 39 | 0.72 | Royal Challengers Bengaluru | India |
| 6 | Axar Patel | 0.60 | 1.57 | 2.22 | 4.36 | 3.09 | 2.84 | 0.25 | 446 | 92 | 7.38 | 7.97 | 24 | 0.46 | Delhi Capitals | India |
| 7 | Mohsin Khan | 1.72 | 1.24 | 0.66 | 2.23 | 7.42 | 7.29 | 0.13 | 151 | 26 | 8.41 | 8.51 | 11 | 1.00 | Lucknow Super Giants |  |
| 8 | Nathan Ellis | 1.69 | 1.08 | 0.82 | 1.61 | 7.28 | 7.19 | 0.09 | 247 | 33 | 8.49 | 8.06 | 16 | 0.40 | Chennai Super Kings | Australia |
| 9 | Josh Hazlewood | 2.23 | 1.56 | 0.04 | 0.32 | 9.38 | 9.35 | 0.02 | 333 | 49 | 8.17 | 8.29 | 24 | 0.68 | Royal Challengers Bengaluru | Australia |
| 10 | Jason Holder | 2.22 | 0.15 | 1.15 | -0.04 | 9.35 | 9.34 | 0.00 | 422 | 65 | 9.60 | 8.79 | 24 | 0.33 | Gujarat Titans | West Indies |

Level, normal and delta are in NRAE per 100 balls. Standardised component columns (z_) are in the units the composite adds up.

Figures: `top10_batters.png`, `top10_bowlers.png` (ratings with 80% intervals); `level_vs_normal_batters.png`, `level_vs_normal_bowlers.png` (who lifts and who dips, top 20 labelled); `sensitivity_heatmap_batters.png`, `sensitivity_heatmap_bowlers.png`.

**Dips under pressure in the top 20.** A top-20 player is flagged when his delta is clearly negative. No top-20 player has a standardised delta at or below -1. Players whose delta is negative in at least half of the bootstrap resamples: Jason Holder (bowler, rank 10, P(delta<0) 0.51). These players rank highly on overall quality, not on rising under pressure.

**Face-validity audit, no overrides** (`face_validity.csv`). The 15 highest-volume death-over batters and bowlers and where each sits:

| role | player_name | death_over_balls | eligible | rank | rating | boot_top10_prob | note |
|---|---|---|---|---|---|---|---|
| batter | Hardik Pandya | 647 | yes | 120 | -0.56 | 0.00 |  |
| batter | Rinku Singh | 584 | yes | 23 | 0.76 | 0.14 |  |
| batter | Tim David | 570 | yes | 3 | 2.01 | 0.75 |  |
| batter | Namboori Tilak Varma | 543 | yes | 4 | 2.00 | 0.71 |  |
| batter | Axar Patel | 525 | yes | 152 | -1.45 | 0.00 |  |
| batter | Rovman Powell | 520 | yes | 12 | 1.13 | 0.24 |  |
| batter | David Miller | 496 | yes | 107 | -0.42 | 0.00 |  |
| batter | Shimron Hetmyer | 487 | yes | 102 | -0.39 | 0.00 |  |
| batter | Shivam Dube | 467 | yes | 76 | -0.11 | 0.00 |  |
| batter | Ravindra Jadeja | 467 | yes | 71 | -0.08 | 0.00 |  |
| batter | Nicholas Pooran | 429 | yes | 16 | 0.99 | 0.26 |  |
| batter | Dinesh Karthik | 429 | no |  |  |  | not eligible: no appearance in 2025 or 2026 |
| batter | Heinrich Klaasen | 393 | yes | 6 | 1.53 | 0.46 |  |
| batter | Romario Shepherd | 368 | yes | 60 | 0.05 | 0.03 |  |
| batter | Suryakumar Yadav | 361 | yes | 19 | 0.84 | 0.24 |  |
| bowler | Arshdeep Singh | 1037 | yes | 26 | 0.75 | 0.14 |  |
| bowler | Bhuvneshwar Kumar | 691 | yes | 5 | 1.82 | 0.62 |  |
| bowler | Harshal Patel | 649 | yes | 48 | 0.31 | 0.01 |  |
| bowler | Mustafizur Rahman | 622 | yes | 40 | 0.54 | 0.04 |  |
| bowler | Jason Holder | 617 | yes | 10 | 1.15 | 0.26 |  |
| bowler | Avesh Khan | 599 | yes | 57 | 0.14 | 0.01 |  |
| bowler | Rashid Khan | 516 | yes | 4 | 2.10 | 0.68 |  |
| bowler | Jasprit Bumrah | 514 | yes | 1 | 3.19 | 0.97 |  |
| bowler | Matheesha Pathirana | 501 | yes | 13 | 1.05 | 0.15 |  |
| bowler | T Natarajan | 442 | yes | 27 | 0.73 | 0.05 |  |
| bowler | Romario Shepherd | 419 | yes | 150 | -0.92 | 0.00 |  |
| bowler | Mohammed Siraj | 414 | yes | 86 | -0.10 | 0.01 |  |
| bowler | Sam Curran | 408 | yes | 101 | -0.20 | 0.00 |  |
| bowler | Mukesh Kumar | 408 | yes | 51 | 0.26 | 0.01 |  |
| bowler | Maheesh Theekshana | 403 | yes | 45 | 0.38 | 0.04 |  |

Several famous finishers sit in the bottom half, even with the role-aware baseline that no longer penalises them for facing many first balls. Their numbers are reported, not adjusted. The usual reasons in the tables are a pressure strike rate no better than the state-adjusted baseline for the death overs, where the baseline is already very high, and dismissals in high-leverage chases that cost win probability.

## 8. Robustness and persistence

**Bootstrap.** 1000 resamples of matches, full rating recomputed each time with the eligible set held fixed. Mean rank, 80% rank interval and top-10 probability for every eligible player are in `batter_ratings.csv` and `bowler_ratings.csv`; the top 10 are in section 1.

**Sensitivity grid** (`sensitivity_configs.csv`, `sensitivity_membership.csv`). 14 structural configurations, each crossed with the primary weights plus 200 weight vectors drawn from a Dirichlet centred on them (concentration 20).

| config | batter eligible | bowler eligible | batter top-10 overlap | bowler top-10 overlap | batter spearman | bowler spearman |
|---|---|---|---|---|---|---|
| A primary | 153 | 166 | 10 | 10 | 1.00 | 1.00 |
| B contested-state rule | 105 | 133 | 3 | 7 | 0.67 | 0.77 |
| C leverage pct >= 90 | 89 | 108 | 5 | 8 | 0.83 | 0.83 |
| D leverage pct >= 70 | 167 | 182 | 8 | 8 | 0.89 | 0.91 |
| E death overs, WP 0.2-0.8 | 87 | 97 | 3 | 8 | 0.69 | 0.80 |
| F global leverage pct >= 80 | 143 | 152 | 8 | 7 | 0.82 | 0.79 |
| eligibility x0.5 | 211 | 230 | 10 | 8 | 1.00 | 1.00 |
| eligibility x1.5 | 116 | 129 | 9 | 10 | 1.00 | 1.00 |
| recency off | 153 | 166 | 7 | 9 | 0.91 | 0.95 |
| A-team and associates at full weight | 153 | 166 | 10 | 9 | 0.99 | 0.99 |
| A-team and associate opposition removed | 145 | 159 | 10 | 10 | 0.99 | 0.99 |
| IPL only | 79 | 84 | 4 | 7 | 0.86 | 0.85 |
| T20I only | 89 | 98 | 6 | 5 | 0.85 | 0.86 |
| empirical Bayes estimator | 153 | 166 | 5 | 5 | 0.80 | 0.83 |

**Persistence** (`persistence.csv`, figure `persistence_scatter.png`). Ratings are computed separately in two halves of the matches and correlated across players eligible in both (half thresholds).

| role | split | n_common | spearman_rating | spearman_level | spearman_impact | spearman_consistency | spearman_delta | spearman_brown_rating |
|---|---|---|---|---|---|---|---|---|
| batter | season split (2022-24 vs 2025-26) | 96.00 | 0.03 | 0.11 | -0.05 | 0.09 | -0.09 | 0.06 |
| batter | odd/even match split | 145.00 | 0.07 | 0.11 | 0.00 | 0.00 | 0.03 | 0.13 |
| batter | random half splits (mean of 20) | 139.30 | 0.06 | 0.13 | -0.01 | 0.05 | 0.02 | 0.11 |
| bowler | season split (2022-24 vs 2025-26) | 104.00 | 0.20 | 0.24 | 0.15 | 0.11 | 0.07 | 0.34 |
| bowler | odd/even match split | 153.00 | 0.09 | 0.15 | 0.15 | -0.01 | -0.07 | 0.16 |
| bowler | random half splits (mean of 20) | 150.65 | 0.12 | 0.19 | 0.10 | 0.08 | -0.01 | 0.21 |

This is the most important caveat in the document. Split-half Spearman correlation of the rating is 0.06 for batters and 0.12 for bowlers (Spearman-Brown full-sample reliability 0.11 and 0.21). The Level component persists weakly; the pressure delta (0.02 and -0.01) and consistency do not persist. In plain words: who is good is measurable, who is specifically better under pressure than their own normal is mostly not, at these sample sizes. The ranking is a best estimate, not a stable ordering, and the intervals in section 1 should be taken seriously.

**Decision rule** (`decision_rule.csv`). Fixed in advance: a primary top-10 player with grid top-10 frequency below 0.40 is replaced by the best-ranked outsider at or above it.

| role | player_id | player_name | primary_rank | grid_top10_prob | action |
|---|---|---|---|---|---|
| batter |  |  |  |  | no primary top-10 player below the threshold; primary list kept |
| bowler | 2633 | Jason Holder | 10.00 | 0.31 | below threshold, kept (no outsider at or above threshold) |

## 9. Rajasthan Royals fit layer

This layer sits on top of the rankings and does not feed them. Public context and its sourcing are in `context/rr_auction_context.md`. Overseas status is derived (national side in the mapping file is not India). Availability is "unknown, check after retention list" for every player: the retention and release deadline was moved to 17 November 2026 and the lists were not public when this was written. The IPL 2027 auction is a mini-auction on 16 December 2026 in Goa, the last before a mega auction ahead of 2028.

**RR under pressure by phase** (`rr_team_profile.csv`, figure `rr_gap.png`). NRAE per 100 pressure balls, RR minus the league, with RR's rank among the ten teams. The table file also splits chasing and setting.

| discipline | year | phase | rr_balls | rr_nrae_per100 | league_mean_nrae_per100 | rr_minus_league | rr_rank_of_teams |
|---|---|---|---|---|---|---|---|
| batting | 2025 | powerplay | 63 | 57.8 | 12.9 | 44.9 | 1 |
| batting | 2025 | middle | 150 | 14.5 | 9.2 | 5.3 | 6 |
| batting | 2025 | death | 170 | -15.5 | -5.8 | -9.7 | 8 |
| batting | 2026 | powerplay | 89 | 70.0 | 7.0 | 63.0 | 1 |
| batting | 2026 | middle | 98 | -10.5 | 1.9 | -12.4 | 7 |
| batting | 2026 | death | 97 | 16.9 | 8.2 | 8.7 | 4 |
| bowling | 2025 | powerplay | 91 | -8.2 | -11.3 | 3.1 | 6 |
| bowling | 2025 | middle | 105 | -41.8 | -8.6 | -33.2 | 10 |
| bowling | 2025 | death | 146 | -5.9 | 6.3 | -12.2 | 8 |
| bowling | 2026 | powerplay | 122 | -14.9 | -9.2 | -5.7 | 5 |
| bowling | 2026 | middle | 119 | 11.8 | -1.9 | 13.7 | 2 |
| bowling | 2026 | death | 137 | -25.0 | -8.4 | -16.6 | 6 |

In IPL 2026 RR ranked seventh or worse of ten under pressure in: batting in the middle overs (-12 per 100 balls, rank 7). Below the league average but ranked better than seventh: bowling in the powerplay overs (-6, rank 5), bowling in the death overs (-17, rank 6). Each cell holds about 100 to 150 balls, so treat single cells as indications. Public season reviews name two weaknesses, the middle order and the lack of a second strike bowler beside Jofra Archer. The data agree on the middle-order batting. They also show pressure bowling below the league in at least one phase, consistent with the second point.

**RR regulars in IPL 2026** (`rr_incumbents.csv`; regular = 7 or more matches):

| player_name | ipl2026_matches | overseas_derived | batter_role | batter_rank | batter_rating | bowler_role | bowler_rank | bowler_rating |
|---|---|---|---|---|---|---|---|---|
| Yashasvi Jaiswal | 16 | no | opener | 40 | 0.40 |  |  |  |
| Dhruv Jurel | 16 | no | middle order/finisher (5+) | 132 | -0.66 |  |  |  |
| Jofra Archer | 16 | yes | middle order/finisher (5+) |  |  | pace, powerplay-leaning | 32 | 0.65 |
| Vaibhav Sooryavanshi | 16 | no | opener | 1 | 2.68 |  |  |  |
| Donovan Ferreira | 15 | yes | middle order/finisher (5+) | 57 | 0.09 |  |  |  |
| Ravindra Jadeja | 14 | no | middle order/finisher (5+) | 71 | -0.08 | spinner | 80 | -0.04 |
| Riyan Parag | 14 | no | top/middle order (3-4) | 36 | 0.48 |  |  |  |
| Nandre Burger | 13 | yes |  |  |  | pace, powerplay-leaning | 96 | -0.17 |
| Brijesh Sharma | 13 | no |  |  |  | pace, death-leaning | 84 | -0.08 |
| Ravi Bishnoi | 9 | no |  |  |  | spinner | 149 | -0.88 |
| Shimron Hetmyer | 8 | yes | middle order/finisher (5+) | 102 | -0.39 |  |  |  |
| Yash Punja | 8 | no |  |  |  | spinner |  |  |
| Dasun Shanaka | 7 | yes | middle order/finisher (5+) | 113 | -0.50 | pace, all phases | 52 | 0.26 |
| Shubham Dubey | 7 | no | middle order/finisher (5+) |  |  |  |  |  |
| Tushar Deshpande | 7 | no |  |  |  | pace, death-leaning | 112 | -0.33 |

**Top-10 players: role, splits and gap** (`rr_fit.csv`, which also covers ranks 11 to 20 and holds the pace/spin, left/right, period and competition splits with their ball counts):

| final_rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | press_sr_vs_pace | press_sr_vs_spin | press_nrae100_2022_24 | press_nrae100_2025_26 | press_nrae100_ipl | press_nrae100_t20i | weakest_rr_regular | rating_gap_vs_weakest | displacement_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | opener | powerplay | Rajasthan Royals | no | 255.9 | 164.7 |  | 79.8 | 112.8 | 6.7 | Yashasvi Jaiswal | 2.3 | already an RR player |
| 2 | Abhishek Sharma | opener | powerplay | Sunrisers Hyderabad | no | 195.3 | 218.0 | -3.5 | 58.6 | 8.8 | 71.9 | Yashasvi Jaiswal | 1.9 | upgrade on point estimate, inside the noise |
| 3 | Tim David | middle order/finisher (5+) | death | Royal Challengers Bengaluru | yes | 206.1 | 128.3 | 16.9 | 75.1 | 29.8 | 33.3 | Dhruv Jurel | 2.7 | would displace (80% intervals do not overlap) |
| 4 | Namboori Tilak Varma | middle order/finisher (5+) | middle | Mumbai Indians | no | 184.8 | 129.8 | 14.4 | 42.6 | 15.6 | 43.4 | Dhruv Jurel | 2.7 | would displace (80% intervals do not overlap) |
| 5 | Phil Salt | opener | powerplay | Royal Challengers Bengaluru | yes | 184.0 | 133.9 | 33.4 | 38.7 | 56.4 | 20.6 | Yashasvi Jaiswal | 1.3 | upgrade on point estimate, inside the noise |
| 6 | Heinrich Klaasen | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 184.4 | 182.4 | 35.2 | 39.4 | 36.8 | 36.1 | Dhruv Jurel | 2.2 | would displace (80% intervals do not overlap) |
| 7 | Sahibzada Farhan | opener | powerplay | not in an IPL 2026 squad | yes | 144.0 | 194.3 | -81.3 | 39.6 |  | 28.3 | Yashasvi Jaiswal | 1.0 | upgrade on point estimate, inside the noise |
| 8 | Pathum Nissanka | opener | powerplay | Delhi Capitals | yes | 157.2 | 146.4 | 3.2 | 48.6 | 12.6 | 30.7 | Yashasvi Jaiswal | 1.0 | upgrade on point estimate, inside the noise |
| 9 | Shreyas Iyer | top/middle order (3-4) | middle | Punjab Kings | no | 159.5 | 147.2 | -34.7 | 39.8 | 18.3 | -3.4 | Riyan Parag | 0.9 | upgrade on point estimate, inside the noise |
| 10 | Fakhar Zaman | top/middle order (3-4) | powerplay | not in an IPL 2026 squad | yes | 203.7 | 125.6 | 46.8 | 45.1 |  | 46.0 | Riyan Parag | 0.8 | upgrade on point estimate, inside the noise |

| final_rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | press_econ_vs_rhb | press_econ_vs_lhb | press_nrae100_2022_24 | press_nrae100_2025_26 | press_nrae100_ipl | press_nrae100_t20i | weakest_rr_regular | rating_gap_vs_weakest | displacement_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah | pace, death-leaning | powerplay | Mumbai Indians | no | 7.5 | 6.0 | 28.1 | 38.8 | 23.1 | 71.7 | Tushar Deshpande | 3.5 | would displace (80% intervals do not overlap) |
| 2 | Varun Chakravarthy | spinner | middle | Kolkata Knight Riders | no | 7.1 | 8.5 | 34.2 | 17.4 | 12.2 | 68.0 | Ravi Bishnoi | 3.5 | would displace (80% intervals do not overlap) |
| 3 | Sunil Narine | spinner | middle | Kolkata Knight Riders | no | 6.4 | 7.2 | 23.8 | 19.4 | 22.3 |  | Ravi Bishnoi | 3.1 | would displace (80% intervals do not overlap) |
| 4 | Rashid Khan | spinner | middle | Gujarat Titans | yes | 7.1 | 7.9 | 38.0 | 25.5 | 31.5 | 39.3 | Ravi Bishnoi | 3.0 | would displace (80% intervals do not overlap) |
| 5 | Bhuvneshwar Kumar | pace, death-leaning | powerplay | Royal Challengers Bengaluru | no | 8.7 | 9.1 | 24.2 | 29.2 | 37.2 | -3.2 | Tushar Deshpande | 2.2 | would displace (80% intervals do not overlap) |
| 6 | Axar Patel | spinner | middle | Delhi Capitals | no | 6.9 | 8.8 | 26.1 | 26.7 | 21.8 | 30.3 | Ravi Bishnoi | 2.6 | would displace (80% intervals do not overlap) |
| 7 | Mohsin Khan | pace, powerplay-leaning | powerplay | Lucknow Super Giants | no | 9.5 | 6.5 | 21.4 | 141.6 | 45.3 |  | Nandre Burger | 1.6 | upgrade on point estimate, inside the noise |
| 8 | Nathan Ellis | pace, death-leaning | death | Chennai Super Kings | yes | 8.6 | 8.3 | 25.2 | 16.3 | 19.6 | 23.0 | Tushar Deshpande | 1.7 | upgrade on point estimate, inside the noise |
| 9 | Josh Hazlewood | pace, powerplay-leaning | powerplay | Royal Challengers Bengaluru | yes | 7.3 | 9.5 | 10.6 | 17.3 | 17.7 | 5.2 | Nandre Burger | 1.5 | upgrade on point estimate, inside the noise |
| 10 | Jason Holder | pace, death-leaning | death | Gujarat Titans | yes | 10.1 | 9.0 | -0.9 | -0.0 | 3.8 | -2.8 | Tushar Deshpande | 1.5 | upgrade on point estimate, inside the noise |

**Auction shortlist.** Players from the top 20 of either group who are not already at RR, whose main phase is one of RR's 2026 pressure gap cells and whose bootstrap top-10 probability is at least 0.10:

| group | rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | boot_top10_prob | displacement_call | availability |
|---|---|---|---|---|---|---|---|---|---|
| batter | 4 | Namboori Tilak Varma | middle order/finisher (5+) | middle | Mumbai Indians | no | 0.71 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| batter | 6 | Heinrich Klaasen | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 0.46 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| batter | 9 | Shreyas Iyer | top/middle order (3-4) | middle | Punjab Kings | no | 0.35 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 13 | Towhid Hridoy | top/middle order (3-4) | middle | not in an IPL 2026 squad | yes | 0.26 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 16 | Nicholas Pooran | top/middle order (3-4) | middle | Lucknow Super Giants | yes | 0.26 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 19 | Suryakumar Yadav | top/middle order (3-4) | middle | Mumbai Indians | no | 0.24 | upgrade on point estimate, inside the noise | unknown, check after retention list |

**Squad-rule constraints.** This is a mini-auction, so a pick has to fit the slots and purse RR has left after releases; RR's remaining purse and open slots for 2027 are unknown until the lists are out. Sourced in the context file: a squad holds at least 18 and at most 25 players with at most 8 overseas (2026 cycle, several outlets; assumed unchanged for 2027), and RR filled all 25 places in 2026. The limit of 4 overseas players in an XI rests on one weak source and is assumed. RR's 2026 regulars already include 5 derived-overseas players, so an overseas pick has to displace one of them in the XI; Indian options on the shortlist are worth more to RR than their rating alone says. A mini-auction also has no right-to-match and few slots, which favours a short, role-specific shortlist over a long list.

"Would displace" is used only where the candidate's 80% rating interval lies entirely above the incumbent's. Everything else is described as inside the noise.

## 10. Limitations and where the model is least certain

- **Low persistence.** See section 8. The rating has limited repeatability and the pressure-specific components have almost none.
- **Extras reconstruction.** Bye and leg-bye run values are not stored. Innings totals carry a mean error of about 2.1 runs with a long tail. The chase target is anchored to the result so the end of a chase is exact, but first-innings scores and early-chase required rates are not.
- **Small pressure samples.** The pressure sample is a fifth of the data. A typical eligible batter has 140 pressure balls (median) and a typical bowler 132.
- **Selection into high-leverage states.** Good teams reach close finishes more often and choose who bats and bowls in them. Team-season and opponent effects absorb part of this, not all.
- **Run value of a wicket at the death is small.** In run terms a wicket with two overs left costs little, so NRAE gives little credit for death wickets. WPA carries that value, at 25% of the rating.
- **First-innings pressure is weakly identified.** First-innings win probability barely moves away from 0.5, so the first-innings pressure sample is the top fifth of a narrow range.
- **Team context and role.** A finisher and an opener face different jobs. The role-aware baseline corrects the largest part (new batters score well below set batters), not all of it.
- **No pitch, weather, dew, boundary-size or fielding data.** Ball-speed is missing on about 39% of rows and is not used.
- **Fixed eligible set in the bootstrap** and penalties fixed at their cross-validated values: intervals are somewhat too narrow.
- **Outside cross-checks.** One data error was found and corrected (match 20190). Sooryavanshi's IPL 2026 line rebuilt from the ball data (776 runs, average 48.5, strike rate 237.3) matches published figures, and RR's 2026 playoff results match the reports. Five unflagged short matches were found by internal checks. Other data errors of the same kind may remain undetected.

## 11. Honest weak spots

- The rating mostly measures how good a player is in general and only slightly how much he lifts under pressure. The data cannot support a stronger clutch claim, and section 8 shows why.
- The shift in batting and bowling outcomes from Normal to pressure almost disappears once phase, innings and wickets are held fixed. The pressure definition separates stakes, not behaviour.
- 10 of the 20 listed players finish in the top 10 in fewer than half of the bootstrap resamples: Heinrich Klaasen (0.46), Sahibzada Farhan (0.43), Pathum Nissanka (0.42), Shreyas Iyer (0.35), Fakhar Zaman (0.16), Axar Patel (0.48), Mohsin Khan (0.44), Nathan Ellis (0.35), Josh Hazlewood (0.37), Jason Holder (0.26). The lower half of each list is close to interchangeable with ranks 11 to 25.
- The smallest pressure sample in the lists is Vaibhav Sooryavanshi with 85 pressure balls. He qualifies under the pre-registered thresholds and is kept; his interval is wide.
- The ridge and empirical Bayes estimators agree on the composite but only moderately on Level (section 5). Restricting to one competition changes the lists: top-10 overlap with the primary is IPL only, batters 4 of 10; T20I only, batters 6 of 10; IPL only, bowlers 7 of 10; T20I only, bowlers 5 of 10.
- The fitted extras values improve on the 1-run rule by a few hundredths of a run. The calibration is reported because it was required, not because it matters much.
- Several of the highest-volume death-over players rank poorly (section 7). The model may be right, or the baseline may still be unfair to their role. This was not adjusted by hand.

## 12. Reproduction

```bash
pip install -r requirements.txt
```

```bash
python run_all.py
```

```bash
python -m pytest -q tests
```

About 6 minutes on 4 cores for the full pipeline from the raw CSVs. Seeds are fixed in `config.json`. A run from a fresh clone reproduced every table byte for byte (DECISIONS.md, phase 2a). `python src/phase2_experiments.py` re-runs the model comparisons (about 40 minutes).

## 13. Open questions and next steps

- Check the retention lists and replace the availability column, then re-run stage 09.
- Obtain true innings totals or extras run values; the reconstruction error would vanish.
- Add leagues beyond the IPL and T20Is to raise pressure samples; persistence is limited by sample size.
- Model the pressure delta hierarchically by role (finishers, death bowlers) instead of per player; a role-level effect may be estimable where a player-level one is not.
- Use ball-tracking variables (length, line) to separate execution from outcome for bowlers.
- Test whether a win-probability model with team strength changes leverage for mismatched fixtures.

## What changed in phase 2

Phase 2 audited the phase 1 pipeline, then tried model changes and judged each only on model-quality evidence: out-of-fold log loss and calibration, split-half reliability of the ratings (mean Spearman over 20 random match-half splits), season-split persistence and bootstrap stability. The identity of the players in the lists was never a criterion. Phase 1 results are kept in `outputs/phase1/`. The full log is in `docs/DECISIONS.md`, sections C and D.

Model-quality scorecard (`phase2_experiments.csv`). Higher is better for the split-half, persistence, leverage-validity and top-10 probability columns; lower is better for log loss, RMSE and rank-interval width.

| tag | verdict | wp_logloss | wp_logloss_inn2 | lev_spearman_abs_wpa | bat_xruns_rmse | bowl_xruns_rmse | bat_splithalf_rating | bowl_splithalf_rating | bat_season_persistence | bowl_season_persistence | bat_boot_top10_prob_of_top10 | bowl_boot_top10_prob_of_top10 | bat_boot_rank_iqr80_top20 | bowl_boot_rank_iqr80_top20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | reference | 0.5220 | 0.3976 | 0.5695 | 1.7200 | 1.7554 | 0.0801 | 0.1132 | 0.0590 | 0.1752 | 0.5770 | 0.5210 | 44.9050 | 50.5900 |
| target_recon | rejected | 0.5236 | 0.4008 | 0.5670 | 1.7202 | 1.7557 | 0.0665 | 0.1166 | 0.0586 | 0.1827 | 0.5770 | 0.4970 | 45.2900 | 58.2850 |
| wp_gbm | rejected | 0.5327 | 0.4164 | 0.5915 | 1.7200 | 1.7554 | 0.1723 | 0.1062 | 0.1571 | 0.2319 | 0.5905 | 0.4710 | 44.4400 | 59.2400 |
| wp_nomom | rejected | 0.5221 | 0.3981 | 0.4566 | 1.7200 | 1.7554 | 0.1258 | 0.2235 | -0.0213 | 0.2415 | 0.4735 | 0.5745 | 44.9750 | 40.6750 |
| lev_rms | rejected | 0.5220 | 0.3976 | 0.5103 | 1.7200 | 1.7554 | 0.0253 | 0.1548 | -0.0727 | 0.1692 | 0.4830 | 0.5190 | 52.8700 | 56.3700 |
| role_aware | ADOPTED | 0.5220 | 0.3976 | 0.5695 | 1.7107 | 1.7459 | 0.0600 | 0.1190 | 0.0324 | 0.2036 | 0.5510 | 0.5860 | 47.4900 | 46.6700 |
| opp_ts | rejected | 0.5220 | 0.3976 | 0.5695 | 1.7200 | 1.7554 | 0.0755 | 0.1157 | 0.0552 | 0.1790 | 0.5780 | 0.5725 | 43.8950 | 48.0050 |
| prior_sd | rejected | 0.5220 | 0.3976 | 0.5695 | 1.7200 | 1.7554 | 0.0529 | 0.1548 | 0.0782 | 0.2145 | 0.5620 | 0.5265 | 50.2150 | 49.6050 |
| role_prior | rejected | 0.5220 | 0.3976 | 0.5695 | 1.7107 | 1.7459 | 0.0352 | 0.1451 | 0.0684 | 0.2191 | 0.5300 | 0.5745 | 52.3900 | 48.5950 |
| role_prior_opp | rejected | 0.5220 | 0.3976 | 0.5695 | 1.7107 | 1.7459 | 0.0282 | 0.1493 | 0.0510 | 0.2228 | 0.5370 | 0.5760 | 52.4600 | 47.3100 |

- **base**: phase 1 primary specification. Phase 1 specification, the reference for every comparison.
- **target_recon**: handover target: reconstructed first-innings total + 1 instead of result-anchored. Out-of-fold log loss is worse (0.5236 against 0.5220; chases 0.4008 against 0.3976). The result-anchored target stays.
- **wp_gbm**: originally pre-registered monotone LightGBM win-probability model. Out-of-fold log loss is clearly worse (0.5327 against 0.5220) and calibration is worse. Batter split-half reliability happens to be higher with it, but the rule requires the model's own metric to improve first, and a worse win-probability model is not a sound basis for leverage.
- **wp_nomom**: win probability without momentum features. Log loss is the same (0.5221), the calibration gap is larger (0.036 against 0.026) and leverage tracks realised swings less well (Spearman 0.46 against 0.57). No improvement in its own metric, so not adopted, although bowler reliability was higher.
- **lev_rms**: leverage as root-mean-square swing instead of mean absolute swing. Leverage tracks realised win-probability swings less well (Spearman 0.51 against 0.57) and batter reliability falls.
- **role_aware**: baseline knows balls already faced by the striker and batting position. Every baseline metric improves: batter expected-runs RMSE 1.7200 to 1.7107, bowler 1.7554 to 1.7459, both wicket log losses fall, and the ridge cross-validated error falls for both groups (7.599 to 7.577 and 7.612 to 7.590). Split-half reliability moves within two standard errors (batters 0.080 to 0.060, bowlers 0.113 to 0.119). Bootstrap stability is better for bowlers and slightly worse for batters. Adopted under the rule as a post-hoc change.
- **opp_ts**: ridge adds an opposition-team-by-season strength term. Split-half reliability does not move beyond noise (batters 0.080 to 0.076, bowlers 0.113 to 0.116). The bowler and striker effects already carry opposition strength.
- **prior_sd**: components scaled by between-player prior SD instead of z-scored after shrinkage. Bowler reliability rises by more than two standard errors (0.113 to 0.155) but batter reliability falls (0.080 to 0.053) and batter bootstrap stability is worse (rank-interval width 44.9 to 50.2). The rule requires stability not to worsen, so the pre-registered z-scoring stays. The audit concern about re-inflated noise is real in principle but the data do not show a gain from fixing it.
- **role_prior**: role-aware baseline and prior-SD scaling together. On top of the role-aware baseline the scaling change again helps bowlers a little and hurts batters; neither move clears two standard errors.
- **role_prior_opp**: role-aware baseline, prior-SD scaling and opposition term. No gain over the role-aware baseline alone.

Standard error of the split-half figure across the 20 splits is about 0.016 (batters) and 0.017 (bowlers); differences smaller than about twice that are not evidence.

**Top-10 lists before and after** (`outputs/phase1/top10_*.csv` versus `outputs/tables/top10_*.csv`):

*Batters*

| Rank | Phase 1 | Phase 2 (final) |
|---|---|---|
| 1 | Vaibhav Sooryavanshi | Vaibhav Sooryavanshi |
| 2 | Namboori Tilak Varma | Abhishek Sharma |
| 3 | Abhishek Sharma | Tim David |
| 4 | Tim David | Namboori Tilak Varma |
| 5 | Sahibzada Farhan | Phil Salt |
| 6 | Heinrich Klaasen | Heinrich Klaasen |
| 7 | Phil Salt | Sahibzada Farhan |
| 8 | Pathum Nissanka | Pathum Nissanka |
| 9 | Shreyas Iyer | Shreyas Iyer |
| 10 | Prabhsimran Singh | Fakhar Zaman |

- Namboori Tilak Varma: rank 2 to 4, stays in the top 10. Rating 2.54 to 2.00; the component that moved most is level (-0.39 rating points).
- Abhishek Sharma: rank 3 to 2, stays in the top 10. Rating 2.42 to 2.25; the component that moved most is consistency (-0.14 rating points).
- Tim David: rank 4 to 3, stays in the top 10. Rating 1.69 to 2.01; the component that moved most is consistency (+0.15 rating points).
- Sahibzada Farhan: rank 5 to 7, stays in the top 10. Rating 1.67 to 1.41; the component that moved most is level (-0.12 rating points).
- Phil Salt: rank 7 to 5, stays in the top 10. Rating 1.62 to 1.70; the component that moved most is consistency (+0.06 rating points).
- Prabhsimran Singh: rank 10 to 11, leaves the top 10. Rating 1.45 to 1.22; the component that moved most is level (-0.12 rating points).
- Fakhar Zaman: rank 11 to 10, enters the top 10. Rating 1.37 to 1.28; the component that moved most is level (-0.14 rating points).

*Bowlers*

| Rank | Phase 1 | Phase 2 (final) |
|---|---|---|
| 1 | Jasprit Bumrah | Jasprit Bumrah |
| 2 | Varun Chakravarthy | Varun Chakravarthy |
| 3 | Sunil Narine | Sunil Narine |
| 4 | Rashid Khan | Rashid Khan |
| 5 | Axar Patel | Bhuvneshwar Kumar |
| 6 | Mohsin Khan | Axar Patel |
| 7 | Bhuvneshwar Kumar | Mohsin Khan |
| 8 | Nathan Ellis | Nathan Ellis |
| 9 | Josh Hazlewood | Josh Hazlewood |
| 10 | Taskin Ahmed | Jason Holder |

- Axar Patel: rank 5 to 6, stays in the top 10. Rating 1.63 to 1.73; the component that moved most is consistency (+0.08 rating points).
- Mohsin Khan: rank 6 to 7, stays in the top 10. Rating 1.54 to 1.46; the component that moved most is level (-0.18 rating points).
- Bhuvneshwar Kumar: rank 7 to 5, stays in the top 10. Rating 1.45 to 1.82; the component that moved most is level (+0.25 rating points).
- Taskin Ahmed: rank 10 to 11, leaves the top 10. Rating 1.16 to 1.09; the component that moved most is consistency (-0.06 rating points).
- Jason Holder: rank 11 to 10, enters the top 10. Rating 1.12 to 1.15; the component that moved most is consistency (-0.10 rating points).

Every difference has the same cause, the role-aware baseline (post-hoc change P-1). It stops charging batters for the slow first balls of an innings and stops crediting bowlers for bowling to batters who have just arrived. Ratings move by up to about half a point and neighbours swap places. A player can gain a place while his own rating falls, when a neighbour falls further. Ranks 9 to 12 are separated by a few hundredths of a rating point in both versions.

**Reading the scorecard honestly.** Split-half reliability swings by more than its split-to-split standard error whenever the pressure sample itself changes (compare the win-probability variants), so the standard error understates the real uncertainty of this yardstick. No variant lifts reliability to a level that would change the main caveat of this document: the rating is a noisy best estimate. One change was adopted, the role-aware baseline, because it makes the baseline measurably more accurate and removes a bias against batters who face many first balls. Everything else in the pre-registered specification is unchanged.

## Exact dropdown selections

**Batters**

1. Vaibhav Sooryavanshi (50284)
2. Abhishek Sharma (6281)
3. Tim David (6396)
4. Namboori Tilak Varma (7897)
5. Phil Salt (5553)
6. Heinrich Klaasen (4260)
7. Sahibzada Farhan (3091)
8. Pathum Nissanka (6931)
9. Shreyas Iyer (3647)
10. Fakhar Zaman (2921)

**Bowlers**

1. Jasprit Bumrah (2933)
2. Varun Chakravarthy (6256)
3. Sunil Narine (781)
4. Rashid Khan (4722)
5. Bhuvneshwar Kumar (360)
6. Axar Patel (2876)
7. Mohsin Khan (6669)
8. Nathan Ellis (7920)
9. Josh Hazlewood (830)
10. Jason Holder (2633)
