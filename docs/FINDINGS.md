# FINDINGS: who delivers under pressure

Every number below is read from a file in `outputs/tables/` when the pipeline runs (`src/11_report.py`). The file is named next to each table. Figures are in `outputs/figures/`.

## 1. Result in one page

Rating is the composite pressure rating. The interval is the 80% interval from a match bootstrap (1000 resamples). P(top 10) boot is the share of bootstrap resamples in which the player finishes in the top 10. P(top 10) grid is the share of sensitivity-grid configurations in which he does.

### Top 10 batters (`top10_batters.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) boot | P(top 10) grid | Pressure balls |
|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi (50284) | 2.77 | 1.03 to 3.21 | 1 to 14 | 0.87 | 0.50 | 85 |
| 2 | Namboori Tilak Varma (7897) | 2.54 | 1.02 to 2.65 | 1 to 15 | 0.84 | 1.00 | 514 |
| 3 | Abhishek Sharma (6281) | 2.42 | 0.60 to 2.89 | 1 to 30 | 0.73 | 0.70 | 300 |
| 4 | Tim David (6396) | 1.69 | 0.58 to 2.03 | 2 to 31 | 0.56 | 0.66 | 321 |
| 5 | Sahibzada Farhan (3091) | 1.67 | 0.44 to 1.89 | 3 to 39 | 0.51 | 0.57 | 128 |
| 6 | Heinrich Klaasen (4260) | 1.66 | 0.54 to 1.84 | 3 to 33 | 0.50 | 0.80 | 256 |
| 7 | Phil Salt (5553) | 1.62 | 0.58 to 1.82 | 3 to 32 | 0.53 | 0.71 | 200 |
| 8 | Pathum Nissanka (6931) | 1.59 | 0.31 to 1.98 | 3 to 47 | 0.49 | 0.66 | 263 |
| 9 | Shreyas Iyer (3647) | 1.53 | 0.20 to 1.93 | 3 to 56 | 0.43 | 0.68 | 293 |
| 10 | Prabhsimran Singh (7216) | 1.45 | 0.46 to 1.45 | 6 to 38 | 0.29 | 0.58 | 243 |

1. **Vaibhav Sooryavanshi**: Leads on pressure level (+4.7) and lift over own normal level (+2.2); strike rate 238 under pressure against 220 otherwise, 202 runs and 4 dismissals in 85 pressure balls.
2. **Namboori Tilak Varma**: Leads on lift over own normal level (+5.1) and win-probability impact (+2.4); strike rate 167 under pressure against 137 otherwise, 856 runs and 20 dismissals in 514 pressure balls.
3. **Abhishek Sharma**: Leads on pressure level (+4.2) and lift over own normal level (+2.1); strike rate 202 under pressure against 185 otherwise, 606 runs and 18 dismissals in 300 pressure balls.
4. **Tim David**: Leads on pressure level (+2.5) and lift over own normal level (+1.3); strike rate 192 under pressure against 172 otherwise, 615 runs and 23 dismissals in 321 pressure balls.
5. **Sahibzada Farhan**: Leads on consistency (+1.9) and pressure level (+1.7); strike rate 165 under pressure against 132 otherwise, 211 runs and 7 dismissals in 128 pressure balls.
6. **Heinrich Klaasen**: Leads on pressure level (+2.2) and consistency (+1.5); strike rate 184 under pressure against 163 otherwise, 470 runs and 14 dismissals in 256 pressure balls.
7. **Phil Salt**: Leads on pressure level (+2.3) and consistency (+1.8); strike rate 170 under pressure against 171 otherwise, 340 runs and 7 dismissals in 200 pressure balls.
8. **Pathum Nissanka**: Leads on consistency (+1.9) and lift over own normal level (+1.9); strike rate 153 under pressure against 133 otherwise, 403 runs and 13 dismissals in 263 pressure balls.
9. **Shreyas Iyer**: Leads on win-probability impact (+2.2) and lift over own normal level (+1.9); strike rate 155 under pressure against 154 otherwise, 454 runs and 12 dismissals in 293 pressure balls.
10. **Prabhsimran Singh**: Leads on consistency (+3.4) and lift over own normal level (+2.4); strike rate 176 under pressure against 154 otherwise, 427 runs and 6 dismissals in 243 pressure balls.

### Top 10 bowlers (`top10_bowlers.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) boot | P(top 10) grid | Pressure balls |
|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah (2933) | 3.10 | 1.48 to 2.79 | 1 to 5 | 0.98 | 1.00 | 366 |
| 2 | Varun Chakravarthy (6256) | 2.11 | 0.95 to 2.04 | 2 to 16 | 0.78 | 0.93 | 401 |
| 3 | Sunil Narine (781) | 1.99 | 0.86 to 1.88 | 2 to 19 | 0.70 | 0.92 | 351 |
| 4 | Rashid Khan (4722) | 1.78 | 0.53 to 1.94 | 2 to 39 | 0.54 | 0.78 | 484 |
| 5 | Axar Patel (2876) | 1.63 | 0.46 to 1.79 | 3 to 42 | 0.46 | 0.62 | 446 |
| 6 | Mohsin Khan (6669) | 1.54 | 0.34 to 2.14 | 2 to 51 | 0.49 | 0.73 | 151 |
| 7 | Bhuvneshwar Kumar (360) | 1.45 | 0.32 to 1.94 | 2 to 53 | 0.47 | 0.72 | 560 |
| 8 | Nathan Ellis (7920) | 1.37 | 0.38 to 1.64 | 4 to 48 | 0.39 | 0.78 | 247 |
| 9 | Josh Hazlewood (830) | 1.16 | 0.16 to 1.58 | 4 to 67 | 0.29 | 0.52 | 333 |
| 10 | Taskin Ahmed (2681) | 1.16 | 0.27 to 1.20 | 10 to 57 | 0.11 | 0.37 | 247 |

1. **Jasprit Bumrah**: Leads on consistency (+4.1) and pressure level (+3.3); economy 7.07 under pressure against 7.15 otherwise, 20 wickets in 366 pressure balls.
2. **Varun Chakravarthy**: Leads on consistency (+3.1) and win-probability impact (+2.1); economy 7.59 under pressure against 8.16 otherwise, 25 wickets in 401 pressure balls.
3. **Sunil Narine**: Leads on win-probability impact (+2.3) and pressure level (+2.2); economy 6.74 under pressure against 6.80 otherwise, 14 wickets in 351 pressure balls.
4. **Rashid Khan**: Leads on lift over own normal level (+2.3) and win-probability impact (+2.1); economy 7.40 under pressure against 7.40 otherwise, 41 wickets in 484 pressure balls.
5. **Axar Patel**: Leads on lift over own normal level (+4.3) and consistency (+1.8); economy 7.38 under pressure against 7.97 otherwise, 24 wickets in 446 pressure balls.
6. **Mohsin Khan**: Leads on pressure level (+2.2) and lift over own normal level (+2.1); economy 8.41 under pressure against 8.51 otherwise, 11 wickets in 151 pressure balls.
7. **Bhuvneshwar Kumar**: Leads on pressure level (+2.0) and lift over own normal level (+1.5); economy 8.87 under pressure against 8.04 otherwise, 39 wickets in 560 pressure balls.
8. **Nathan Ellis**: Leads on pressure level (+1.7) and lift over own normal level (+1.4); economy 8.49 under pressure against 8.06 otherwise, 16 wickets in 247 pressure balls.
9. **Josh Hazlewood**: Leads on pressure level (+1.9) and win-probability impact (+1.6); economy 8.17 under pressure against 8.29 otherwise, 24 wickets in 333 pressure balls.
10. **Taskin Ahmed**: Leads on lift over own normal level (+2.9) and win-probability impact (+2.1); economy 6.89 under pressure against 8.36 otherwise, 24 wickets in 247 pressure balls.

The bootstrap interval of a top-ranked player usually sits below his point rating. That is expected: the players at the top of a noisy ranking are partly there by luck, and resampling the matches pulls them back. Read the interval as the honest range.

## 2. Pressure definition and validation

**Definition.** Pressure is how much the next ball can move the match. For every delivery the out-of-fold win-probability model scores the state after each possible next-ball outcome (dot, 1, 2, 3, 4, 6, wicket, wide, no-ball). Leverage is the expected absolute change in win probability, weighting outcomes by their frequency in that phase and innings, divided by the global mean so an average ball has leverage 1. The pressure score is the percentile of leverage among all deliveries of the same innings number. Tiers: Low below 50, Normal 50 to 80, High 80 to 95, Extreme above. The pressure sample is score at or above 80.

**Why it is meaningful.** One number learned from match outcomes combines required rate, wickets in hand, balls left and closeness. A dead game has win probability near 0 or 1, nothing the next ball does can move it, and leverage is low without any hand-set cutoff.

**Does leverage measure what it claims?** Leverage is computed before the ball; the realised absolute win-probability change is observed after. Their Spearman correlation is 0.57. The top 20% of deliveries by leverage move win probability by 3.8 points on average, the bottom 50% by 0.9 points (`leverage_validity.csv`).

Outcomes by tier (`pressure_validation.csv`, table = tier overall; figure `pressure_tier_metrics.png`):

| tier | deliveries | strike_rate | dot_pct | boundary_pct | wickets per 100 balls | economy | mean_leverage | mean |WP change| (pts) |
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
- **Wicket check.** 418/419 matches agree with the result string. The exception is match 20190, where the result string says 6 wickets and the ball data shows 5 wickets down. This check does not depend on extras.
- **Extras calibration** (`extras_calibration.csv`). Fitted run values: wide 1.08, no-ball 1.00, other no-ball 1.00, leg bye 1.08, bye 1.69. On 396 clean run-margin matches the mean absolute error of the reconstructed margin is 2.14 runs (1-run rule 2.17; out of sample 2.17). The margin is exact in 32% of matches with the 1-run rule and within 2 runs in 57% with the fitted values. The fitted values barely beat the 1-run rule: the residual error is not about the average value of an extra, it is unrecorded bye and leg-bye runs and occasional missing deliveries.
- **Why the target is anchored to the result.** In 42% of chases won by wickets the reconstructed chasing total is still below the reconstructed target at the end. The chase target is therefore recovered from the result string (see section 5). Required-rate features early in a chase still carry the reconstruction error of roughly 2 runs per innings.
- **Exclusions.** no ball data: 16.0; reduced (revised fields or DLS text): 38.0; no winner (no result / abandoned) with balls, not reduced: 14.0; first innings incomplete without flag: 5.0; second innings unresolved or result inconsistent: 1.0. Clean matches kept: 809.0. Super-over deliveries dropped: 38.
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

**Baselines without player identity** (`expected_model_metrics.csv`). Out-of-fold LightGBM models give expected bat runs and dismissal probability per ball faced, and expected runs charged and wicket probability per bowler slot. Features: innings, phase, balls left, wickets lost, current and required rate and their gap, venue average, competition tier, pace or spin, bowling type, batter hand, no-ball and free-hit flags.

| model | n | metric | oof | phase_mean_baseline | mean_actual | mean_pred |
|---|---|---|---|---|---|---|
| batter xRuns | 185928 | RMSE | 1.7200 | 1.7381 | 1.3934 | 1.3954 |
| batter xWkt | 185928 | log loss | 0.2079 | 0.2088 | 0.0542 | 0.0553 |
| bowler xRuns | 185122 | RMSE | 1.7554 | 1.7739 | 1.4473 | 1.4484 |
| bowler xWkt | 185122 | log loss | 0.2050 | 0.2054 | 0.0529 | 0.0540 |

**Wicket value in runs** (`resource_table.csv`). Expected remaining first-innings runs are fitted as R_w(b) = a_w (1 - exp(-b / t_w)) with a non-crossing penalty. The value of a wicket is the drop in expected remaining runs from w to w+1 wickets down. Examples: 120 balls left, 0 down: 12.4 runs; 60 balls left, 0 down: 2.2 runs; 24 balls left, 0 down: 0.0 runs; 120 balls left, 3 down: 12.6 runs; 60 balls left, 3 down: 7.7 runs; 24 balls left, 3 down: 3.3 runs; 120 balls left, 6 down: 17.1 runs; 60 balls left, 6 down: 13.3 runs; 24 balls left, 6 down: 6.1 runs.

**Ball-level credit.**

- Batter NRAE (net runs above expected) = (bat runs - expected runs) - wicket value x (dismissed - expected dismissal). The dismissal is charged to the dismissed player; non-striker run outs and dismissals off wides are dismissal-only records. Retired out costs nothing.
- Bowler NRAE = (expected runs - runs charged) + wicket value x (bowler wicket - expected wicket). Wides and no-balls are charged, byes and leg byes are not. Run outs and retirements are not credited.
- WPA = change in out-of-fold win probability across the ball, to the striker and with opposite sign to the bowler.

**Player estimates.** A weighted crossed ridge regression on ball-level NRAE with: player normal effect, player pressure delta, opponent effect (bowler for batters, striker for bowlers), own-team-by-season effect, venue, tier and an unpenalised pressure indicator. Penalties chosen by 5-fold cross-validation grouped by match (`ridge_cv.csv`): batters main 1000, delta 3000; bowlers main 300, delta 30000. The cross-validated error surface is almost flat in the delta penalty and for bowlers the choice sits at the largest value in the grid: the data contain very little information about individual pressure deltas.

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
| bat | level: ridge vs empirical Bayes | 153 | 0.47 |
| bat | delta: ridge vs empirical Bayes | 153 | 0.84 |
| bat | composite rating: ridge vs empirical Bayes | 153 | 0.85 |
| bat | top-10 overlap: ridge vs empirical Bayes | 10 | 0.50 |
| bowl | level: ridge vs empirical Bayes | 166 | 0.46 |
| bowl | delta: ridge vs empirical Bayes | 166 | 0.93 |
| bowl | composite rating: ridge vs empirical Bayes | 166 | 0.84 |
| bowl | top-10 overlap: ridge vs empirical Bayes | 10 | 0.60 |

The Level correlation is below the 0.8 the specification asked us to investigate. The cause is structural, not a bug: the ridge Level is normal effect plus delta and borrows strength from all of a player's balls, while the empirical Bayes Level uses pressure balls only, about a fifth of the sample. The two answer slightly different questions and the second is much noisier.

## 6. Fairness choices

- **Eligibility.** Batters: at least 60 pressure balls faced and 12 pressure innings. Bowlers: at least 48 pressure balls and 10 pressure spells. Both: at least 150 balls in total and an appearance in 2025 or 2026. 153 batters and 166 bowlers qualify, so no threshold was lowered.
- **Sample size.** Shrinkage (ridge, empirical Bayes, beta-binomial) pulls small samples toward the pool mean, so a short hot streak cannot top the list on its own.
- **Recency.** Weights halve every 24 months back from 2026-11-01.
- **Opposition.** The ridge estimates each player against the specific opponents he met and absorbs team strength by season. Deliveries against associate-nation opposition and all A-team tournament deliveries weigh 0.5. An associate player facing a full member keeps full weight.
- **IPL versus T20I.** Both are pooled with a tier term in every model. IPL-only and T20I-only ratings are run as sensitivity configurations (section 8).
- **Weak-opposition check.** Largest share of pressure balls against associate or A-team opposition among the top-10 batters: 9%; among the top-10 bowlers: 8% (`top10_batters.csv`, `top10_bowlers.csv`).

## 7. Evidence for the top 10

**Batters** (`top10_batters.csv`; all eligible players in `batter_ratings.csv`):

| final_rank | player_name | z_level | z_impact | z_consistency | z_delta | level | normal | delta | n_press_balls | n_press_innings | press_sr | normal_sr | press_avg | press_share_ipl | ipl_2026_team | national_team |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | 4.74 | 0.86 | 1.64 | 2.19 | 23.70 | 22.21 | 1.49 | 85 | 19 | 237.65 | 219.76 | 50.50 | 0.69 | Rajasthan Royals | India |
| 2 | Namboori Tilak Varma | 1.79 | 2.40 | 2.29 | 5.06 | 10.28 | 7.03 | 3.24 | 514 | 79 | 166.54 | 137.04 | 42.80 | 0.57 | Mumbai Indians | India |
| 3 | Abhishek Sharma | 4.18 | 0.41 | 1.70 | 2.06 | 21.17 | 19.76 | 1.41 | 300 | 75 | 202.00 | 185.38 | 33.67 | 0.67 | Sunrisers Hyderabad | India |
| 4 | Tim David | 2.51 | 1.05 | 1.11 | 1.32 | 13.54 | 12.59 | 0.95 | 321 | 56 | 191.59 | 171.95 | 26.74 | 0.60 | Royal Challengers Bengaluru | Australia |
| 5 | Sahibzada Farhan | 1.69 | 1.50 | 1.93 | 1.59 | 9.80 | 8.68 | 1.12 | 128 | 25 | 164.84 | 132.15 | 30.14 | 0.00 |  | Pakistan |
| 6 | Heinrich Klaasen | 2.22 | 1.06 | 1.54 | 1.35 | 12.21 | 11.23 | 0.98 | 256 | 48 | 183.59 | 163.34 | 33.57 | 0.87 | Sunrisers Hyderabad | South Africa |
| 7 | Phil Salt | 2.26 | 0.51 | 1.85 | 1.44 | 12.39 | 11.36 | 1.03 | 200 | 41 | 170.00 | 171.12 | 48.57 | 0.41 | Royal Challengers Bengaluru | England |
| 8 | Pathum Nissanka | 1.90 | 0.65 | 1.91 | 1.91 | 10.74 | 9.43 | 1.31 | 263 | 46 | 153.23 | 133.10 | 31.00 | 0.23 | Delhi Capitals | Sri Lanka |
| 9 | Shreyas Iyer | 0.98 | 2.17 | 1.51 | 1.92 | 6.59 | 5.26 | 1.32 | 293 | 52 | 154.95 | 154.48 | 37.83 | 0.68 | Punjab Kings | India |
| 10 | Prabhsimran Singh | 0.50 | 0.87 | 3.38 | 2.39 | 4.36 | 2.76 | 1.61 | 243 | 42 | 175.72 | 154.27 | 71.17 | 0.98 | Punjab Kings | India |

**Bowlers** (`top10_bowlers.csv`; all eligible players in `bowler_ratings.csv`):

| final_rank | player_name | z_level | z_impact | z_consistency | z_delta | level | normal | delta | n_press_balls | n_press_innings | press_econ | normal_econ | press_wkts | press_share_ipl | ipl_2026_team | national_team |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah | 3.29 | 2.41 | 4.05 | 2.46 | 27.13 | 26.99 | 0.13 | 366 | 56 | 7.07 | 7.15 | 20 | 0.77 | Mumbai Indians | India |
| 2 | Varun Chakravarthy | 1.89 | 2.08 | 3.14 | 1.41 | 16.39 | 16.31 | 0.08 | 401 | 64 | 7.59 | 8.16 | 25 | 0.74 | Kolkata Knight Riders | India |
| 3 | Sunil Narine | 2.17 | 2.27 | 2.16 | 0.82 | 18.57 | 18.53 | 0.05 | 351 | 54 | 6.74 | 6.80 | 14 | 1.00 | Kolkata Knight Riders |  |
| 4 | Rashid Khan | 1.47 | 2.08 | 1.62 | 2.33 | 13.19 | 13.07 | 0.13 | 484 | 80 | 7.40 | 7.40 | 41 | 0.69 | Gujarat Titans | Afghanistan |
| 5 | Axar Patel | 0.56 | 1.57 | 1.83 | 4.31 | 6.22 | 5.99 | 0.23 | 446 | 92 | 7.38 | 7.97 | 24 | 0.46 | Delhi Capitals | India |
| 6 | Mohsin Khan | 2.16 | 1.24 | 0.25 | 2.09 | 18.50 | 18.38 | 0.11 | 151 | 26 | 8.41 | 8.51 | 11 | 1.00 | Lucknow Super Giants |  |
| 7 | Bhuvneshwar Kumar | 2.00 | 0.84 | 1.08 | 1.47 | 17.22 | 17.14 | 0.08 | 560 | 78 | 8.87 | 8.04 | 39 | 0.72 | Royal Challengers Bengaluru | India |
| 8 | Nathan Ellis | 1.66 | 1.08 | 1.13 | 1.37 | 14.68 | 14.61 | 0.08 | 247 | 33 | 8.49 | 8.06 | 16 | 0.40 | Chennai Super Kings | Australia |
| 9 | Josh Hazlewood | 1.88 | 1.56 | 0.08 | 0.05 | 16.33 | 16.33 | 0.01 | 333 | 49 | 8.17 | 8.29 | 24 | 0.68 | Royal Challengers Bengaluru | Australia |
| 10 | Taskin Ahmed | -0.49 | 2.12 | 1.95 | 2.88 | -1.77 | -1.93 | 0.16 | 247 | 34 | 6.89 | 8.36 | 24 | 0.00 |  | Bangladesh |

Level, normal and delta are in NRAE per 100 balls. Standardised component columns (z_) are in the units the composite adds up.

Figures: `top10_batters.png`, `top10_bowlers.png` (ratings with 80% intervals); `level_vs_normal_batters.png`, `level_vs_normal_bowlers.png` (who lifts and who dips, top 20 labelled); `sensitivity_heatmap_batters.png`, `sensitivity_heatmap_bowlers.png`.

**Dips under pressure in the top 20.** A top-20 player is flagged when his delta is clearly negative. No top-20 player has a standardised delta at or below -1. Players whose delta is negative in at least half of the bootstrap resamples: Jason Holder (bowler, rank 11, P(delta<0) 0.63). These players rank highly on overall quality, not on rising under pressure.

**Face-validity audit, no overrides** (`face_validity.csv`). The 15 highest-volume death-over batters and bowlers and where each sits:

| role | player_name | death_over_balls | eligible | rank | rating | boot_top10_prob | note |
|---|---|---|---|---|---|---|---|
| batter | Hardik Pandya | 647 | yes | 138 | -0.77 | 0.00 |  |
| batter | Rinku Singh | 584 | yes | 20 | 0.85 | 0.16 |  |
| batter | Tim David | 570 | yes | 4 | 1.69 | 0.56 |  |
| batter | Namboori Tilak Varma | 543 | yes | 2 | 2.54 | 0.84 |  |
| batter | Axar Patel | 525 | yes | 153 | -1.59 | 0.00 |  |
| batter | Rovman Powell | 520 | yes | 12 | 1.25 | 0.31 |  |
| batter | David Miller | 496 | yes | 113 | -0.47 | 0.00 |  |
| batter | Shimron Hetmyer | 487 | yes | 131 | -0.70 | 0.00 |  |
| batter | Shivam Dube | 467 | yes | 86 | -0.21 | 0.00 |  |
| batter | Ravindra Jadeja | 467 | yes | 67 | -0.06 | 0.00 |  |
| batter | Nicholas Pooran | 429 | yes | 21 | 0.82 | 0.16 |  |
| batter | Dinesh Karthik | 429 | no |  |  |  | not eligible: no appearance in 2025 or 2026 |
| batter | Heinrich Klaasen | 393 | yes | 6 | 1.66 | 0.50 |  |
| batter | Romario Shepherd | 368 | yes | 93 | -0.29 | 0.01 |  |
| batter | Suryakumar Yadav | 361 | yes | 16 | 0.97 | 0.25 |  |
| bowler | Arshdeep Singh | 1037 | yes | 21 | 0.87 | 0.15 |  |
| bowler | Bhuvneshwar Kumar | 691 | yes | 7 | 1.45 | 0.47 |  |
| bowler | Harshal Patel | 649 | yes | 53 | 0.25 | 0.01 |  |
| bowler | Mustafizur Rahman | 622 | yes | 45 | 0.38 | 0.02 |  |
| bowler | Jason Holder | 617 | yes | 11 | 1.12 | 0.21 |  |
| bowler | Avesh Khan | 599 | yes | 59 | 0.20 | 0.01 |  |
| bowler | Rashid Khan | 516 | yes | 4 | 1.78 | 0.54 |  |
| bowler | Jasprit Bumrah | 514 | yes | 1 | 3.10 | 0.98 |  |
| bowler | Matheesha Pathirana | 501 | yes | 12 | 1.10 | 0.19 |  |
| bowler | T Natarajan | 442 | yes | 31 | 0.66 | 0.05 |  |
| bowler | Romario Shepherd | 419 | yes | 130 | -0.59 | 0.00 |  |
| bowler | Mohammed Siraj | 414 | yes | 84 | -0.08 | 0.01 |  |
| bowler | Sam Curran | 408 | yes | 95 | -0.17 | 0.00 |  |
| bowler | Mukesh Kumar | 408 | yes | 69 | 0.10 | 0.01 |  |
| bowler | Maheesh Theekshana | 403 | yes | 52 | 0.27 | 0.02 |  |

Several famous finishers sit in the bottom half. Their numbers are reported, not adjusted. The usual reasons in the tables are a pressure strike rate no better than the state-adjusted baseline for the death overs, where the baseline is already very high, and dismissals in high-leverage chases that cost win probability.

## 8. Robustness and persistence

**Bootstrap.** 1000 resamples of matches, full rating recomputed each time with the eligible set held fixed. Mean rank, 80% rank interval and top-10 probability for every eligible player are in `batter_ratings.csv` and `bowler_ratings.csv`; the top 10 are in section 1.

**Sensitivity grid** (`sensitivity_configs.csv`, `sensitivity_membership.csv`). 14 structural configurations, each crossed with the primary weights plus 200 weight vectors drawn from a Dirichlet centred on them (concentration 20).

| config | batter eligible | bowler eligible | batter top-10 overlap | bowler top-10 overlap | batter spearman | bowler spearman |
|---|---|---|---|---|---|---|
| A primary | 153 | 166 | 10 | 10 | 1.00 | 1.00 |
| B contested-state rule | 105 | 133 | 3 | 7 | 0.67 | 0.76 |
| C leverage pct >= 90 | 89 | 108 | 5 | 7 | 0.85 | 0.83 |
| D leverage pct >= 70 | 167 | 182 | 8 | 8 | 0.89 | 0.91 |
| E death overs, WP 0.2-0.8 | 87 | 97 | 4 | 7 | 0.68 | 0.78 |
| F global leverage pct >= 80 | 143 | 152 | 8 | 6 | 0.80 | 0.79 |
| eligibility x0.5 | 211 | 230 | 10 | 8 | 1.00 | 1.00 |
| eligibility x1.5 | 116 | 129 | 9 | 10 | 1.00 | 1.00 |
| recency off | 153 | 166 | 8 | 9 | 0.92 | 0.95 |
| A-team and associates at full weight | 153 | 166 | 10 | 9 | 0.99 | 0.99 |
| A-team and associate opposition removed | 145 | 159 | 10 | 9 | 0.99 | 0.99 |
| IPL only | 79 | 84 | 5 | 5 | 0.85 | 0.85 |
| T20I only | 89 | 98 | 5 | 6 | 0.85 | 0.87 |
| empirical Bayes estimator | 153 | 166 | 5 | 6 | 0.85 | 0.84 |

**Persistence** (`persistence.csv`, figure `persistence_scatter.png`). Ratings are computed separately in two halves of the matches and correlated across players eligible in both (half thresholds).

| role | split | n_common | spearman_rating | spearman_level | spearman_impact | spearman_consistency | spearman_delta | spearman_brown_rating |
|---|---|---|---|---|---|---|---|---|
| batter | season split (2022-24 vs 2025-26) | 96.00 | 0.06 | 0.17 | -0.05 | 0.19 | -0.10 | 0.11 |
| batter | odd/even match split | 145.00 | 0.10 | 0.13 | 0.00 | 0.08 | 0.01 | 0.18 |
| batter | random half splits (mean of 20) | 139.30 | 0.08 | 0.15 | -0.01 | 0.13 | 0.03 | 0.15 |
| bowler | season split (2022-24 vs 2025-26) | 104.00 | 0.18 | 0.22 | 0.15 | 0.02 | 0.06 | 0.30 |
| bowler | odd/even match split | 153.00 | 0.11 | 0.16 | 0.15 | -0.03 | -0.05 | 0.19 |
| bowler | random half splits (mean of 20) | 150.65 | 0.11 | 0.20 | 0.10 | 0.05 | -0.02 | 0.20 |

This is the most important caveat in the document. Split-half Spearman correlation of the rating is 0.08 for batters and 0.11 for bowlers (Spearman-Brown full-sample reliability 0.15 and 0.20). The Level component persists weakly; the pressure delta (0.03 and -0.02) and consistency do not persist. In plain words: who is good is measurable, who is specifically better under pressure than their own normal is mostly not, at these sample sizes. The ranking is a best estimate, not a stable ordering, and the intervals in section 1 should be taken seriously.

**Decision rule** (`decision_rule.csv`). Fixed in advance: a primary top-10 player with grid top-10 frequency below 0.40 is replaced by the best-ranked outsider at or above it.

| role | player_id | player_name | primary_rank | grid_top10_prob | action |
|---|---|---|---|---|---|
| batter |  |  |  |  | no primary top-10 player below the threshold; primary list kept |
| bowler | 2681 | Taskin Ahmed | 10.00 | 0.37 | below threshold, kept (no outsider at or above threshold) |

## 9. Rajasthan Royals fit layer

This layer sits on top of the rankings and does not feed them. Public context and its sourcing are in `context/rr_auction_context.md`. Overseas status is derived (national side in the mapping file is not India). Availability is "unknown, check after retention list" for every player: retention lists were due on 15 November 2026 and were not public when this was written.

**RR under pressure by phase** (`rr_team_profile.csv`, figure `rr_gap.png`). NRAE per 100 pressure balls, RR minus the league, with RR's rank among the ten teams. The table file also splits chasing and setting.

| discipline | year | phase | rr_balls | rr_nrae_per100 | league_mean_nrae_per100 | rr_minus_league | rr_rank_of_teams |
|---|---|---|---|---|---|---|---|
| batting | 2025 | powerplay | 63 | 50.5 | 11.5 | 38.9 | 2 |
| batting | 2025 | middle | 150 | 13.4 | 8.3 | 5.0 | 6 |
| batting | 2025 | death | 170 | -19.8 | -6.4 | -13.4 | 8 |
| batting | 2026 | powerplay | 89 | 67.8 | 7.3 | 60.5 | 1 |
| batting | 2026 | middle | 98 | -9.5 | -0.4 | -9.0 | 7 |
| batting | 2026 | death | 97 | 16.2 | 9.1 | 7.1 | 4 |
| bowling | 2025 | powerplay | 91 | -11.6 | -9.6 | -2.0 | 7 |
| bowling | 2025 | middle | 105 | -40.2 | -7.7 | -32.5 | 10 |
| bowling | 2025 | death | 146 | -6.4 | 6.9 | -13.2 | 8 |
| bowling | 2026 | powerplay | 122 | -16.5 | -8.0 | -8.6 | 7 |
| bowling | 2026 | middle | 119 | 17.7 | -0.3 | 17.9 | 1 |
| bowling | 2026 | death | 137 | -29.6 | -8.6 | -21.0 | 7 |

In IPL 2026 RR ranked seventh or worse under pressure in: bowling in the death (-21 per 100 balls, rank 7), batting in the middle (-9 per 100 balls, rank 7), bowling in the powerplay (-9 per 100 balls, rank 7). Each cell holds about 100 to 150 balls, so treat single cells as indications. The public season reviews point the same way: a soft middle order and no second strike bowler alongside Jofra Archer.

**RR regulars in IPL 2026** (`rr_incumbents.csv`; regular = 7 or more matches):

| player_name | ipl2026_matches | overseas_derived | batter_role | batter_rank | batter_rating | bowler_role | bowler_rank | bowler_rating |
|---|---|---|---|---|---|---|---|---|
| Yashasvi Jaiswal | 16 | no | opener | 41 | 0.39 |  |  |  |
| Dhruv Jurel | 16 | no | middle order/finisher (5+) | 140 | -0.81 |  |  |  |
| Jofra Archer | 16 | yes | middle order/finisher (5+) |  |  | pace, powerplay-leaning | 39 | 0.54 |
| Vaibhav Sooryavanshi | 16 | no | opener | 1 | 2.77 |  |  |  |
| Donovan Ferreira | 15 | yes | middle order/finisher (5+) | 65 | -0.03 |  |  |  |
| Ravindra Jadeja | 14 | no | middle order/finisher (5+) | 67 | -0.06 | spinner | 74 | 0.03 |
| Riyan Parag | 14 | no | top/middle order (3-4) | 30 | 0.64 |  |  |  |
| Nandre Burger | 13 | yes |  |  |  | pace, powerplay-leaning | 80 | -0.02 |
| Brijesh Sharma | 13 | no |  |  |  | pace, death-leaning | 96 | -0.19 |
| Ravi Bishnoi | 9 | no |  |  |  | spinner | 148 | -0.87 |
| Shimron Hetmyer | 8 | yes | middle order/finisher (5+) | 131 | -0.70 |  |  |  |
| Yash Punja | 8 | no |  |  |  | spinner |  |  |
| Dasun Shanaka | 7 | yes | middle order/finisher (5+) | 116 | -0.53 | pace, all phases | 47 | 0.34 |
| Shubham Dubey | 7 | no | middle order/finisher (5+) |  |  |  |  |  |
| Tushar Deshpande | 7 | no |  |  |  | pace, death-leaning | 110 | -0.33 |

**Top-10 players: role, splits and gap** (`rr_fit.csv`, which also covers ranks 11 to 20 and holds the pace/spin, left/right, period and competition splits with their ball counts):

| final_rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | press_sr_vs_pace | press_sr_vs_spin | press_nrae100_2022_24 | press_nrae100_2025_26 | press_nrae100_ipl | press_nrae100_t20i | weakest_rr_regular | rating_gap_vs_weakest | displacement_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | opener | powerplay | Rajasthan Royals | no | 255.9 | 164.7 |  | 88.6 | 124.2 | 5.7 | Yashasvi Jaiswal | 2.4 | already an RR player |
| 2 | Namboori Tilak Varma | middle order/finisher (5+) | middle | Mumbai Indians | no | 184.8 | 129.8 | 17.4 | 51.5 | 21.9 | 50.3 | Dhruv Jurel | 3.3 | would displace (80% intervals do not overlap) |
| 3 | Abhishek Sharma | opener | powerplay | Sunrisers Hyderabad | no | 195.3 | 218.0 | -1.9 | 62.8 | 10.3 | 78.9 | Yashasvi Jaiswal | 2.0 | upgrade on point estimate, inside the noise |
| 4 | Tim David | middle order/finisher (5+) | death | Royal Challengers Bengaluru | yes | 206.1 | 128.3 | 12.8 | 73.9 | 23.0 | 35.3 | Dhruv Jurel | 2.5 | would displace (80% intervals do not overlap) |
| 5 | Sahibzada Farhan | opener | powerplay | not in an IPL 2026 squad | yes | 144.0 | 194.3 | -71.6 | 45.7 |  | 34.7 | Yashasvi Jaiswal | 1.3 | upgrade on point estimate, inside the noise |
| 6 | Heinrich Klaasen | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 184.4 | 182.4 | 33.1 | 43.4 | 38.9 | 22.6 | Dhruv Jurel | 2.5 | would displace (80% intervals do not overlap) |
| 7 | Phil Salt | opener | powerplay | Royal Challengers Bengaluru | yes | 184.0 | 133.9 | 33.9 | 41.2 | 58.8 | 20.8 | Yashasvi Jaiswal | 1.2 | upgrade on point estimate, inside the noise |
| 8 | Pathum Nissanka | opener | powerplay | Delhi Capitals | yes | 157.2 | 146.4 | 8.1 | 53.0 | 15.8 | 35.7 | Yashasvi Jaiswal | 1.2 | upgrade on point estimate, inside the noise |
| 9 | Shreyas Iyer | top/middle order (3-4) | middle | Punjab Kings | no | 159.5 | 147.2 | -32.0 | 45.1 | 21.7 | 2.4 | Riyan Parag | 0.9 | upgrade on point estimate, inside the noise |
| 10 | Prabhsimran Singh | opener | powerplay | Punjab Kings | no | 181.6 | 159.4 | 51.6 | 37.5 | 43.0 |  | Yashasvi Jaiswal | 1.1 | upgrade on point estimate, inside the noise |

| final_rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | press_econ_vs_rhb | press_econ_vs_lhb | press_nrae100_2022_24 | press_nrae100_2025_26 | press_nrae100_ipl | press_nrae100_t20i | weakest_rr_regular | rating_gap_vs_weakest | displacement_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah | pace, death-leaning | powerplay | Mumbai Indians | no | 7.5 | 6.0 | 27.0 | 41.1 | 23.1 | 75.4 | Tushar Deshpande | 3.4 | would displace (80% intervals do not overlap) |
| 2 | Varun Chakravarthy | spinner | middle | Kolkata Knight Riders | no | 7.1 | 8.5 | 34.6 | 16.6 | 11.1 | 70.7 | Ravi Bishnoi | 3.0 | would displace (80% intervals do not overlap) |
| 3 | Sunil Narine | spinner | middle | Kolkata Knight Riders | no | 6.4 | 7.2 | 23.6 | 21.1 | 22.8 |  | Ravi Bishnoi | 2.9 | would displace (80% intervals do not overlap) |
| 4 | Rashid Khan | spinner | middle | Gujarat Titans | yes | 7.1 | 7.9 | 39.1 | 25.3 | 31.2 | 41.9 | Ravi Bishnoi | 2.7 | would displace (80% intervals do not overlap) |
| 5 | Axar Patel | spinner | middle | Delhi Capitals | no | 6.9 | 8.8 | 25.0 | 27.4 | 21.1 | 30.5 | Ravi Bishnoi | 2.5 | would displace (80% intervals do not overlap) |
| 6 | Mohsin Khan | pace, powerplay-leaning | powerplay | Lucknow Super Giants | no | 9.5 | 6.5 | 20.3 | 145.7 | 45.3 |  | Nandre Burger | 1.6 | upgrade on point estimate, inside the noise |
| 7 | Bhuvneshwar Kumar | pace, death-leaning | powerplay | Royal Challengers Bengaluru | no | 8.7 | 9.1 | 22.8 | 28.0 | 35.9 | -4.7 | Tushar Deshpande | 1.8 | upgrade on point estimate, inside the noise |
| 8 | Nathan Ellis | pace, death-leaning | death | Chennai Super Kings | yes | 8.6 | 8.3 | 22.2 | 21.7 | 19.2 | 23.8 | Tushar Deshpande | 1.7 | upgrade on point estimate, inside the noise |
| 9 | Josh Hazlewood | pace, powerplay-leaning | powerplay | Royal Challengers Bengaluru | yes | 7.3 | 9.5 | 15.2 | 20.7 | 21.7 | 9.2 | Nandre Burger | 1.2 | upgrade on point estimate, inside the noise |
| 10 | Taskin Ahmed | pace, powerplay-leaning | powerplay | not in an IPL 2026 squad | yes | 7.1 | 6.3 | 41.1 | 41.8 |  | 41.4 | Nandre Burger | 1.2 | upgrade on point estimate, inside the noise |

**Auction shortlist.** Players from the top 20 of either group who are not already at RR, whose main phase is one of RR's 2026 pressure gap cells and whose bootstrap top-10 probability is at least 0.10:

| group | rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | boot_top10_prob | displacement_call | availability |
|---|---|---|---|---|---|---|---|---|---|
| batter | 2 | Namboori Tilak Varma | middle order/finisher (5+) | middle | Mumbai Indians | no | 0.84 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| batter | 6 | Heinrich Klaasen | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 0.50 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| batter | 9 | Shreyas Iyer | top/middle order (3-4) | middle | Punjab Kings | no | 0.43 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 13 | Towhid Hridoy | top/middle order (3-4) | middle | not in an IPL 2026 squad | yes | 0.26 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 16 | Suryakumar Yadav | top/middle order (3-4) | middle | Mumbai Indians | no | 0.25 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 1 | Jasprit Bumrah | pace, death-leaning | powerplay | Mumbai Indians | no | 0.98 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| bowler | 6 | Mohsin Khan | pace, powerplay-leaning | powerplay | Lucknow Super Giants | no | 0.49 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 7 | Bhuvneshwar Kumar | pace, death-leaning | powerplay | Royal Challengers Bengaluru | no | 0.47 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 8 | Nathan Ellis | pace, death-leaning | death | Chennai Super Kings | yes | 0.39 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 9 | Josh Hazlewood | pace, powerplay-leaning | powerplay | Royal Challengers Bengaluru | yes | 0.29 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 10 | Taskin Ahmed | pace, powerplay-leaning | powerplay | not in an IPL 2026 squad | yes | 0.11 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 11 | Jason Holder | pace, death-leaning | death | Gujarat Titans | yes | 0.21 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 12 | Matheesha Pathirana | pace, death-leaning | death | Kolkata Knight Riders | yes | 0.19 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 13 | Eshan Malinga | pace, death-leaning | death | Sunrisers Hyderabad | yes | 0.28 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 15 | Rasikh Salam | pace, death-leaning | death | Royal Challengers Bengaluru | no | 0.17 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 16 | Gerald Coetzee | pace, death-leaning | death | Sunrisers Hyderabad | yes | 0.12 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 17 | Harshit Rana | pace, powerplay-leaning | powerplay | Kolkata Knight Riders | no | 0.12 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 18 | Jacob Duffy | pace, powerplay-leaning | powerplay | Royal Challengers Bengaluru | yes | 0.21 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 19 | Ottneil Baartman | pace, death-leaning | death | not in an IPL 2026 squad | yes | 0.14 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| bowler | 20 | Prince Yadav | pace, all phases | death | Lucknow Super Giants | no | 0.19 | upgrade on point estimate, inside the noise | unknown, check after retention list |

**Squad-rule constraints.** For IPL 2026 a squad held at most 25 players with at most 8 overseas (sourced, see the context file). At most 4 overseas players in an XI is the standard playing condition (not re-verified for 2027). Purse, retention count and whether 2027 is a mini or mega auction are unverified. RR's 2026 regulars already include 5 derived-overseas players, so an overseas pick has to displace one of them in the XI; Indian options on the shortlist are worth more to RR than their rating alone says.

"Would displace" is used only where the candidate's 80% rating interval lies entirely above the incumbent's. Everything else is described as inside the noise.

## 10. Limitations and where the model is least certain

- **Low persistence.** See section 8. The rating has limited repeatability and the pressure-specific components have almost none.
- **Extras reconstruction.** Bye and leg-bye run values are not stored. Innings totals carry a mean error of about 2.1 runs with a long tail. The chase target is anchored to the result so the end of a chase is exact, but first-innings scores and early-chase required rates are not.
- **Small pressure samples.** The pressure sample is a fifth of the data. A typical eligible batter has 140 pressure balls (median) and a typical bowler 132.
- **Selection into high-leverage states.** Good teams reach close finishes more often and choose who bats and bowls in them. Team-season and opponent effects absorb part of this, not all.
- **Run value of a wicket at the death is small.** In run terms a wicket with two overs left costs little, so NRAE gives little credit for death wickets. WPA carries that value, at 25% of the rating.
- **First-innings pressure is weakly identified.** First-innings win probability barely moves away from 0.5, so the first-innings pressure sample is the top fifth of a narrow range.
- **Team context and role.** A finisher and an opener face different jobs. The baseline does not know batting position or how long the batter has been in.
- **No pitch, weather, dew, boundary-size or fielding data.** Ball-speed is missing on about 39% of rows and is not used.
- **Fixed eligible set in the bootstrap** and penalties fixed at their cross-validated values: intervals are somewhat too narrow.
- **The result-string exception** (match 20190) and five unflagged short matches were found by checks; other data errors of the same kind may remain undetected.

## 11. Honest weak spots

- The rating mostly measures how good a player is in general and only slightly how much he lifts under pressure. The data cannot support a stronger clutch claim, and section 8 shows why.
- The shift in batting and bowling outcomes from Normal to pressure almost disappears once phase, innings and wickets are held fixed. The pressure definition separates stakes, not behaviour.
- 10 of the 20 listed players finish in the top 10 in fewer than half of the bootstrap resamples: Heinrich Klaasen (0.50), Pathum Nissanka (0.49), Shreyas Iyer (0.43), Prabhsimran Singh (0.29), Axar Patel (0.46), Mohsin Khan (0.49), Bhuvneshwar Kumar (0.47), Nathan Ellis (0.39), Josh Hazlewood (0.29), Taskin Ahmed (0.11). The lower half of each list is close to interchangeable with ranks 11 to 25.
- The smallest pressure sample in the lists is Vaibhav Sooryavanshi with 85 pressure balls. He qualifies under the pre-registered thresholds and is kept; his interval is wide.
- The ridge and empirical Bayes estimators agree on the composite but only moderately on Level (section 5), and the IPL-only and T20I-only configurations each keep about half of the top 10.
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

About 6 minutes on 4 cores for the full pipeline from the raw CSVs. Seeds are fixed in `config.json`. A run from a fresh clone reproduced every table byte for byte (DECISIONS.md, phase 2a). `python src/phase2_experiments.py` re-runs the model comparisons (about 35 minutes).

## 13. Open questions and next steps

- Check the retention lists and replace the availability column, then re-run stage 09.
- Obtain true innings totals or extras run values; the reconstruction error would vanish.
- Add leagues beyond the IPL and T20Is to raise pressure samples; persistence is limited by sample size.
- Model the pressure delta hierarchically by role (finishers, death bowlers) instead of per player; a role-level effect may be estimable where a player-level one is not.
- Use ball-tracking variables (length, line) to separate execution from outcome for bowlers.
- Test whether a win-probability model with team strength changes leverage for mismatched fixtures.

## What changed in phase 2

Phase 2 audited the phase 1 pipeline, then tried model changes and judged each only on model-quality evidence: out-of-fold log loss and calibration, split-half reliability of the ratings (mean Spearman over 20 random match-half splits), season-split persistence and bootstrap stability. The identity of the players in the lists was never a criterion. Phase 1 results are kept in `outputs/phase1/`. The full log is in `docs/DECISIONS.md`, sections C and D.

**Top-10 lists before and after** (`outputs/phase1/top10_*.csv` versus `outputs/tables/top10_*.csv`):

*Batters*

| Rank | Phase 1 | Phase 2 (final) |
|---|---|---|
| 1 | Vaibhav Sooryavanshi | Vaibhav Sooryavanshi |
| 2 | Namboori Tilak Varma | Namboori Tilak Varma |
| 3 | Abhishek Sharma | Abhishek Sharma |
| 4 | Tim David | Tim David |
| 5 | Sahibzada Farhan | Sahibzada Farhan |
| 6 | Heinrich Klaasen | Heinrich Klaasen |
| 7 | Phil Salt | Phil Salt |
| 8 | Pathum Nissanka | Pathum Nissanka |
| 9 | Shreyas Iyer | Shreyas Iyer |
| 10 | Prabhsimran Singh | Prabhsimran Singh |

- Same ten players. Order unchanged.

*Bowlers*

| Rank | Phase 1 | Phase 2 (final) |
|---|---|---|
| 1 | Jasprit Bumrah | Jasprit Bumrah |
| 2 | Varun Chakravarthy | Varun Chakravarthy |
| 3 | Sunil Narine | Sunil Narine |
| 4 | Rashid Khan | Rashid Khan |
| 5 | Axar Patel | Axar Patel |
| 6 | Mohsin Khan | Mohsin Khan |
| 7 | Bhuvneshwar Kumar | Bhuvneshwar Kumar |
| 8 | Nathan Ellis | Nathan Ellis |
| 9 | Josh Hazlewood | Josh Hazlewood |
| 10 | Taskin Ahmed | Taskin Ahmed |

- Same ten players. Order unchanged.



## Exact dropdown selections

**Batters**

1. Vaibhav Sooryavanshi (50284)
2. Namboori Tilak Varma (7897)
3. Abhishek Sharma (6281)
4. Tim David (6396)
5. Sahibzada Farhan (3091)
6. Heinrich Klaasen (4260)
7. Phil Salt (5553)
8. Pathum Nissanka (6931)
9. Shreyas Iyer (3647)
10. Prabhsimran Singh (7216)

**Bowlers**

1. Jasprit Bumrah (2933)
2. Varun Chakravarthy (6256)
3. Sunil Narine (781)
4. Rashid Khan (4722)
5. Axar Patel (2876)
6. Mohsin Khan (6669)
7. Bhuvneshwar Kumar (360)
8. Nathan Ellis (7920)
9. Josh Hazlewood (830)
10. Taskin Ahmed (2681)
