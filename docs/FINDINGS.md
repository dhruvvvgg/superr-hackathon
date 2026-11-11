# FINDINGS: who delivers under pressure

Every number below is read from a file in `outputs/tables/` when the pipeline runs (`src/11_report.py`). The file is named next to each table. Figures are in `outputs/figures/`.

## 1. Result in one page

Rating is the composite pressure rating. The interval is the 80% interval from a match bootstrap (1000 resamples). P(top 10) boot is the share of bootstrap resamples in which the player finishes in the top 10. P(top 10) grid is the share of sensitivity-grid configurations in which he does.

### Top 10 batters (`top10_batters.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) boot | P(top 10) grid | Pressure balls |
|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi (50284) | 4.23 | 1.71 to 4.71 | 1 to 9 | 0.92 | 0.61 | 85 |
| 2 | Abhishek Sharma (6281) | 3.56 | 1.00 to 4.24 | 1 to 22 | 0.81 | 0.79 | 300 |
| 3 | Namboori Tilak Varma (7897) | 2.87 | 0.97 to 3.51 | 1 to 23 | 0.75 | 0.99 | 514 |
| 4 | Phil Salt (5553) | 2.74 | 1.01 to 3.05 | 2 to 22 | 0.71 | 0.84 | 200 |
| 5 | Tim David (6396) | 2.62 | 0.92 to 3.13 | 2 to 24 | 0.68 | 0.94 | 321 |
| 6 | Ashutosh Sharma (8101) | 2.02 | 0.32 to 2.85 | 3 to 49 | 0.48 | 0.77 | 112 |
| 7 | Suryakumar Yadav (1699) | 1.99 | 0.66 to 2.51 | 3 to 35 | 0.50 | 0.54 | 478 |
| 8 | Heinrich Klaasen (4260) | 1.92 | 0.72 to 2.27 | 4 to 32 | 0.44 | 0.80 | 256 |
| 9 | Pathum Nissanka (6931) | 1.72 | 0.29 to 2.38 | 4 to 52 | 0.37 | 0.61 | 263 |
| 10 | Harry Brook (6280) | 1.62 | 0.24 to 2.21 | 5 to 55 | 0.32 | 0.42 | 140 |

1. **Vaibhav Sooryavanshi**: Rated on leverage-weighted level (+4.2 SD), also high on lift over own normal level (+2.0); strike rate 238 under pressure against 220 otherwise, 202 runs and 4 dismissals in 85 pressure balls.
2. **Abhishek Sharma**: Rated on leverage-weighted level (+3.6 SD), also high on lift over own normal level (+2.9); strike rate 202 under pressure against 185 otherwise, 606 runs and 18 dismissals in 300 pressure balls.
3. **Namboori Tilak Varma**: Rated on leverage-weighted level (+2.9 SD), also high on lift over own normal level (+4.6); strike rate 167 under pressure against 137 otherwise, 856 runs and 20 dismissals in 514 pressure balls.
4. **Phil Salt**: Rated on leverage-weighted level (+2.7 SD), also high on consistency (+1.8); strike rate 170 under pressure against 171 otherwise, 340 runs and 7 dismissals in 200 pressure balls.
5. **Tim David**: Rated on leverage-weighted level (+2.6 SD), also high on lift over own normal level (+2.0); strike rate 192 under pressure against 172 otherwise, 615 runs and 23 dismissals in 321 pressure balls.
6. **Ashutosh Sharma**: Rated on leverage-weighted level (+2.0 SD), also high on lift over own normal level (+2.7); strike rate 181 under pressure against 160 otherwise, 203 runs and 7 dismissals in 112 pressure balls.
7. **Suryakumar Yadav**: Rated on leverage-weighted level (+2.0 SD); strike rate 168 under pressure against 167 otherwise, 804 runs and 24 dismissals in 478 pressure balls.
8. **Heinrich Klaasen**: Rated on leverage-weighted level (+1.9 SD), also high on lift over own normal level (+1.3); strike rate 184 under pressure against 163 otherwise, 470 runs and 14 dismissals in 256 pressure balls.
9. **Pathum Nissanka**: Rated on leverage-weighted level (+1.7 SD), also high on lift over own normal level (+1.4); strike rate 153 under pressure against 133 otherwise, 403 runs and 13 dismissals in 263 pressure balls.
10. **Harry Brook**: Rated on leverage-weighted level (+1.6 SD); strike rate 159 under pressure against 166 otherwise, 223 runs and 10 dismissals in 140 pressure balls.

### Top 10 bowlers (`top10_bowlers.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) boot | P(top 10) grid | Pressure balls |
|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah (2933) | 3.70 | 1.91 to 3.86 | 1 to 8 | 0.94 | 1.00 | 366 |
| 2 | Varun Chakravarthy (6256) | 2.91 | 1.28 to 3.29 | 1 to 17 | 0.76 | 1.00 | 401 |
| 3 | Bhuvneshwar Kumar (360) | 2.68 | 0.77 to 3.47 | 1 to 33 | 0.67 | 0.89 | 560 |
| 4 | Sunil Narine (781) | 2.67 | 1.27 to 2.87 | 2 to 17 | 0.76 | 0.94 | 351 |
| 5 | Rashid Khan (4722) | 2.66 | 1.08 to 3.18 | 2 to 21 | 0.71 | 1.00 | 484 |
| 6 | Josh Hazlewood (830) | 2.38 | 0.85 to 2.91 | 2 to 28 | 0.58 | 0.89 | 333 |
| 7 | Mohsin Khan (6669) | 2.02 | 0.48 to 2.71 | 3 to 45 | 0.44 | 0.86 | 151 |
| 8 | Axar Patel (2876) | 1.97 | 0.48 to 2.59 | 3 to 45 | 0.43 | 0.90 | 446 |
| 9 | Nathan Ellis (7920) | 1.86 | 0.54 to 2.39 | 4 to 42 | 0.36 | 0.81 | 247 |
| 10 | Wanindu Hasaranga (4900) | 1.83 | 0.53 to 2.34 | 5 to 42 | 0.35 | 0.40 | 406 |

1. **Jasprit Bumrah**: Rated on leverage-weighted level (+3.7 SD), also high on lift over own normal level (+2.7); economy 7.07 under pressure against 7.15 otherwise, 20 wickets in 366 pressure balls.
2. **Varun Chakravarthy**: Rated on leverage-weighted level (+2.9 SD), also high on consistency (+2.5); economy 7.59 under pressure against 8.16 otherwise, 25 wickets in 401 pressure balls.
3. **Bhuvneshwar Kumar**: Rated on leverage-weighted level (+2.7 SD), also high on lift over own normal level (+2.1); economy 8.87 under pressure against 8.04 otherwise, 39 wickets in 560 pressure balls.
4. **Sunil Narine**: Rated on leverage-weighted level (+2.7 SD), also high on lift over own normal level (+2.1); economy 6.74 under pressure against 6.80 otherwise, 14 wickets in 351 pressure balls.
5. **Rashid Khan**: Rated on leverage-weighted level (+2.7 SD), also high on lift over own normal level (+3.1); economy 7.40 under pressure against 7.40 otherwise, 41 wickets in 484 pressure balls.
6. **Josh Hazlewood**: Rated on leverage-weighted level (+2.4 SD), also high on win-probability impact (+1.7); economy 8.17 under pressure against 8.29 otherwise, 24 wickets in 333 pressure balls.
7. **Mohsin Khan**: Rated on leverage-weighted level (+2.0 SD), also high on lift over own normal level (+2.1); economy 8.41 under pressure against 8.51 otherwise, 11 wickets in 151 pressure balls.
8. **Axar Patel**: Rated on leverage-weighted level (+2.0 SD), also high on lift over own normal level (+3.8); economy 7.38 under pressure against 7.97 otherwise, 24 wickets in 446 pressure balls.
9. **Nathan Ellis**: Rated on leverage-weighted level (+1.9 SD), also high on lift over own normal level (+1.5); economy 8.49 under pressure against 8.06 otherwise, 16 wickets in 247 pressure balls.
10. **Wanindu Hasaranga**: Rated on leverage-weighted level (+1.8 SD); economy 8.31 under pressure against 7.61 otherwise, 24 wickets in 406 pressure balls.

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

**Player estimates.** A weighted crossed ridge regression on ball-level NRAE with: player normal effect, player pressure delta, opponent effect (bowler for batters, striker for bowlers), own-team-by-season effect, venue, tier and an unpenalised pressure indicator. Penalties chosen by 5-fold cross-validation grouped by match (`ridge_cv.csv`): batters main 3000, delta 30000; bowlers main 3000, delta 30000. The cross-validated error surface is almost flat in the delta penalty and for bowlers the choice sits at the largest value in the grid: the data contain very little information about individual pressure deltas.

**The rating (adopted in phase 3, post-hoc change P-2).** The rating is the leverage-weighted level: the ridge estimate of a player's NRAE per 100 balls in which every ball is weighted by its leverage (weight = leverage to the power 1, normalised), so a ball that can move the match counts more than a ball that cannot, with no cutoff. It is opponent-adjusted by the same ridge and standardised among eligible players. The four-part composite of the specification is still computed and reported (`z_` columns) but carries no weight in the rating, because on held-out data its extra parts did not predict anything (section "What changed in phase 3").

| Component | Spec weight | Rating weight | Definition |
|---|---|---|---|
| Level | 0.40 | 1.00 | ridge estimate, NRAE per 100 balls, opponent-adjusted; leverage-weighted in the rating |
| Impact | 0.25 | 0.00 | pressure WPA per 100 balls, empirical Bayes shrinkage with match-clustered errors |
| Consistency | 0.20 | 0.00 | share of pressure innings or spells with NRAE at or above 0, minus the share clearly bad, beta-binomial shrunk |
| Delta | 0.15 | 0.00 | ridge pressure delta: pressure level minus own normal level |

Components are z-scored among eligible players.

**Cross-check estimator** (`estimator_agreement.csv`). Empirical Bayes shrinkage of raw pressure NRAE (unweighted by leverage):

| role | quantity | n | value |
|---|---|---|---|
| bat | level: ridge vs empirical Bayes | 153 | 0.70 |
| bat | delta: ridge vs empirical Bayes | 153 | 0.83 |
| bat | composite rating: ridge vs empirical Bayes | 153 | 0.70 |
| bat | top-10 overlap: ridge vs empirical Bayes | 10 | 0.40 |
| bowl | level: ridge vs empirical Bayes | 166 | 0.73 |
| bowl | delta: ridge vs empirical Bayes | 166 | 0.83 |
| bowl | composite rating: ridge vs empirical Bayes | 166 | 0.73 |
| bowl | top-10 overlap: ridge vs empirical Bayes | 10 | 0.50 |

The Level correlation is below the 0.8 the specification asked us to investigate. The cause is structural, not a bug: the ridge Level is normal effect plus delta and borrows strength from all of a player's balls, while the empirical Bayes Level uses pressure balls only, about a fifth of the sample. The two answer slightly different questions and the second is much noisier.

## 6. Fairness choices

- **Eligibility.** Batters: at least 60 pressure balls faced and 12 pressure innings. Bowlers: at least 48 pressure balls and 10 pressure spells. Both: at least 150 balls in total and an appearance in 2025 or 2026. 153 batters and 166 bowlers qualify, so no threshold was lowered.
- **Sample size.** Shrinkage (ridge, empirical Bayes, beta-binomial) pulls small samples toward the pool mean, so a short hot streak cannot top the list on its own.
- **Recency.** Weights halve every 24 months back from 2026-11-01.
- **Opposition.** The ridge estimates each player against the specific opponents he met and absorbs team strength by season. Deliveries against associate-nation opposition and all A-team tournament deliveries weigh 0.5. An associate player facing a full member keeps full weight.
- **IPL versus T20I.** Both are pooled with a tier term in every model. IPL-only and T20I-only ratings are run as sensitivity configurations (section 8).
- **Weak-opposition check.** Largest share of pressure balls against associate or A-team opposition among the top-10 batters: 9%; among the top-10 bowlers: 3% (`top10_batters.csv`, `top10_bowlers.csv`).

## 7. Evidence for the top 10

**Batters** (`top10_batters.csv`; all eligible players in `batter_ratings.csv`):

| final_rank | player_name | z_level | z_impact | z_consistency | z_delta | level | normal | delta | n_press_balls | n_press_innings | press_sr | normal_sr | press_avg | press_share_ipl | ipl_2026_team | national_team |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | 4.23 | 1.00 | 1.64 | 2.05 | 15.78 | 15.18 | 0.60 | 85 | 19 | 237.65 | 219.76 | 50.50 | 0.69 | Rajasthan Royals | India |
| 2 | Abhishek Sharma | 3.56 | 0.47 | 0.35 | 2.95 | 13.45 | 12.62 | 0.84 | 300 | 75 | 202.00 | 185.38 | 33.67 | 0.67 | Sunrisers Hyderabad | India |
| 3 | Namboori Tilak Varma | 2.87 | 2.18 | 0.90 | 4.60 | 11.08 | 9.81 | 1.27 | 514 | 79 | 166.54 | 137.04 | 42.80 | 0.57 | Mumbai Indians | India |
| 4 | Phil Salt | 2.74 | 0.09 | 1.83 | 1.20 | 10.64 | 10.27 | 0.37 | 200 | 41 | 170.00 | 171.12 | 48.57 | 0.41 | Royal Challengers Bengaluru | England |
| 5 | Tim David | 2.62 | 1.28 | 1.20 | 1.98 | 10.20 | 9.62 | 0.58 | 321 | 56 | 191.59 | 171.95 | 26.74 | 0.60 | Royal Challengers Bengaluru | Australia |
| 6 | Ashutosh Sharma | 2.02 | 0.95 | 1.22 | 2.74 | 8.13 | 7.35 | 0.78 | 112 | 19 | 181.25 | 160.10 | 29.00 | 0.94 | Delhi Capitals |  |
| 7 | Suryakumar Yadav | 1.99 | -1.13 | 0.06 | -0.06 | 8.02 | 7.99 | 0.03 | 478 | 85 | 168.20 | 167.10 | 33.50 | 0.54 | Mumbai Indians | India |
| 8 | Heinrich Klaasen | 1.92 | 0.04 | 0.86 | 1.28 | 7.81 | 7.42 | 0.39 | 256 | 48 | 183.59 | 163.34 | 33.57 | 0.87 | Sunrisers Hyderabad | South Africa |
| 9 | Pathum Nissanka | 1.72 | 0.28 | 0.82 | 1.43 | 7.09 | 6.66 | 0.43 | 263 | 46 | 153.23 | 133.10 | 31.00 | 0.23 | Delhi Capitals | Sri Lanka |
| 10 | Harry Brook | 1.62 | 0.89 | -0.43 | 0.73 | 6.77 | 6.53 | 0.24 | 140 | 32 | 159.29 | 165.62 | 22.30 | 0.20 |  | England |

**Bowlers** (`top10_bowlers.csv`; all eligible players in `bowler_ratings.csv`):

| final_rank | player_name | z_level | z_impact | z_consistency | z_delta | level | normal | delta | n_press_balls | n_press_innings | press_econ | normal_econ | press_wkts | press_share_ipl | ipl_2026_team | national_team |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah | 3.70 | 1.85 | 1.59 | 2.71 | 13.58 | 12.91 | 0.67 | 366 | 56 | 7.07 | 7.15 | 20 | 0.77 | Mumbai Indians | India |
| 2 | Varun Chakravarthy | 2.91 | 1.36 | 2.50 | 2.49 | 10.81 | 10.20 | 0.62 | 401 | 64 | 7.59 | 8.16 | 25 | 0.74 | Kolkata Knight Riders | India |
| 3 | Bhuvneshwar Kumar | 2.68 | 0.97 | 0.52 | 2.12 | 10.00 | 9.47 | 0.53 | 560 | 78 | 8.87 | 8.04 | 39 | 0.72 | Royal Challengers Bengaluru | India |
| 4 | Sunil Narine | 2.67 | 1.97 | 1.44 | 2.08 | 9.95 | 9.43 | 0.52 | 351 | 54 | 6.74 | 6.80 | 14 | 1.00 | Kolkata Knight Riders |  |
| 5 | Rashid Khan | 2.66 | 1.86 | 1.18 | 3.09 | 9.94 | 9.18 | 0.76 | 484 | 80 | 7.40 | 7.40 | 41 | 0.69 | Gujarat Titans | Afghanistan |
| 6 | Josh Hazlewood | 2.38 | 1.67 | 0.54 | 1.11 | 8.93 | 8.65 | 0.28 | 333 | 49 | 8.17 | 8.29 | 24 | 0.68 | Royal Challengers Bengaluru | Australia |
| 7 | Mohsin Khan | 2.02 | 0.91 | 1.21 | 2.08 | 7.69 | 7.17 | 0.52 | 151 | 26 | 8.41 | 8.51 | 11 | 1.00 | Lucknow Super Giants |  |
| 8 | Axar Patel | 1.97 | 1.45 | 1.13 | 3.82 | 7.52 | 6.58 | 0.93 | 446 | 92 | 7.38 | 7.97 | 24 | 0.46 | Delhi Capitals | India |
| 9 | Nathan Ellis | 1.86 | 0.78 | 1.11 | 1.45 | 7.11 | 6.74 | 0.37 | 247 | 33 | 8.49 | 8.06 | 16 | 0.40 | Chennai Super Kings | Australia |
| 10 | Wanindu Hasaranga | 1.83 | 0.65 | -0.78 | 0.47 | 7.00 | 6.87 | 0.13 | 406 | 55 | 8.31 | 7.61 | 24 | 0.51 | Lucknow Super Giants | Sri Lanka |

Level, normal and delta are in NRAE per 100 balls. Standardised component columns (z_) are in the units the composite adds up.

Figures: `top10_batters.png`, `top10_bowlers.png` (ratings with 80% intervals); `level_vs_normal_batters.png`, `level_vs_normal_bowlers.png` (who lifts and who dips, top 20 labelled); `sensitivity_heatmap_batters.png`, `sensitivity_heatmap_bowlers.png`.

**Dips under pressure in the top 20.** A top-20 player is flagged when his delta is clearly negative. No top-20 player has a standardised delta at or below -1. Players whose delta is negative in at least half of the bootstrap resamples: Jason Holder (bowler, rank 15, P(delta<0) 0.52), Mohammad Nawaz (bowler, rank 16, P(delta<0) 0.51). These players rank highly on overall quality, not on rising under pressure.

**Face-validity audit, no overrides** (`face_validity.csv`). The 15 highest-volume death-over batters and bowlers and where each sits:

| role | player_name | death_over_balls | eligible | rank | rating | boot_top10_prob | note |
|---|---|---|---|---|---|---|---|
| batter | Hardik Pandya | 647 | yes | 129 | -0.85 | 0.00 |  |
| batter | Rinku Singh | 584 | yes | 13 | 1.33 | 0.25 |  |
| batter | Tim David | 570 | yes | 5 | 2.62 | 0.68 |  |
| batter | Namboori Tilak Varma | 543 | yes | 3 | 2.87 | 0.75 |  |
| batter | Axar Patel | 525 | yes | 149 | -1.62 | 0.00 |  |
| batter | Rovman Powell | 520 | yes | 31 | 0.79 | 0.06 |  |
| batter | David Miller | 496 | yes | 83 | -0.24 | 0.01 |  |
| batter | Shimron Hetmyer | 487 | yes | 134 | -0.93 | 0.00 |  |
| batter | Shivam Dube | 467 | yes | 42 | 0.42 | 0.01 |  |
| batter | Ravindra Jadeja | 467 | yes | 117 | -0.66 | 0.00 |  |
| batter | Nicholas Pooran | 429 | yes | 16 | 1.14 | 0.22 |  |
| batter | Dinesh Karthik | 429 | no |  |  |  | not eligible: no appearance in 2025 or 2026 |
| batter | Heinrich Klaasen | 393 | yes | 8 | 1.92 | 0.44 |  |
| batter | Romario Shepherd | 368 | yes | 93 | -0.38 | 0.03 |  |
| batter | Suryakumar Yadav | 361 | yes | 7 | 1.99 | 0.50 |  |
| bowler | Arshdeep Singh | 1037 | yes | 17 | 1.22 | 0.24 |  |
| bowler | Bhuvneshwar Kumar | 691 | yes | 3 | 2.68 | 0.67 |  |
| bowler | Harshal Patel | 649 | yes | 67 | 0.11 | 0.00 |  |
| bowler | Mustafizur Rahman | 622 | yes | 28 | 0.83 | 0.03 |  |
| bowler | Jason Holder | 617 | yes | 15 | 1.28 | 0.16 |  |
| bowler | Avesh Khan | 599 | yes | 85 | -0.05 | 0.01 |  |
| bowler | Rashid Khan | 516 | yes | 5 | 2.66 | 0.71 |  |
| bowler | Jasprit Bumrah | 514 | yes | 1 | 3.70 | 0.94 |  |
| bowler | Matheesha Pathirana | 501 | yes | 23 | 0.98 | 0.07 |  |
| bowler | T Natarajan | 442 | yes | 69 | 0.08 | 0.00 |  |
| bowler | Romario Shepherd | 419 | yes | 165 | -2.11 | 0.00 |  |
| bowler | Mohammed Siraj | 414 | yes | 52 | 0.33 | 0.04 |  |
| bowler | Sam Curran | 408 | yes | 144 | -1.00 | 0.00 |  |
| bowler | Mukesh Kumar | 408 | yes | 102 | -0.28 | 0.00 |  |
| bowler | Maheesh Theekshana | 403 | yes | 64 | 0.14 | 0.01 |  |

Several famous finishers sit in the bottom half, even with the role-aware baseline that no longer penalises them for facing many first balls. Their numbers are reported, not adjusted. The usual reasons in the tables are a pressure strike rate no better than the state-adjusted baseline for the death overs, where the baseline is already very high, and dismissals in high-leverage chases that cost win probability.

## 8. Robustness and persistence

**Bootstrap.** 1000 resamples of matches, full rating recomputed each time with the eligible set held fixed. Mean rank, 80% rank interval and top-10 probability for every eligible player are in `batter_ratings.csv` and `bowler_ratings.csv`; the top 10 are in section 1.

**Sensitivity grid** (`sensitivity_configs.csv`, `sensitivity_membership.csv`). 18 structural configurations, each crossed with the primary weights plus 200 weight vectors drawn from a Dirichlet centred on them (concentration 20).

| config | batter eligible | bowler eligible | batter top-10 overlap | bowler top-10 overlap | batter spearman | bowler spearman |
|---|---|---|---|---|---|---|
| A primary | 153 | 166 | 10 | 10 | 1.00 | 1.00 |
| B contested-state rule | 105 | 133 | 6 | 10 | 1.00 | 1.00 |
| C leverage pct >= 90 | 89 | 108 | 9 | 10 | 1.00 | 1.00 |
| D leverage pct >= 70 | 167 | 182 | 10 | 10 | 1.00 | 1.00 |
| E death overs, WP 0.2-0.8 | 87 | 97 | 6 | 10 | 1.00 | 1.00 |
| F global leverage pct >= 80 | 143 | 152 | 10 | 10 | 1.00 | 1.00 |
| no leverage weighting | 153 | 166 | 6 | 6 | 0.80 | 0.88 |
| leverage weight power 0.5 | 153 | 166 | 8 | 8 | 0.95 | 0.97 |
| leverage weight power 2 | 153 | 166 | 6 | 9 | 0.84 | 0.82 |
| spec weights 0.40/0.25/0.20/0.15 | 153 | 166 | 10 | 10 | 0.83 | 0.86 |
| eligibility x0.5 | 211 | 230 | 10 | 10 | 1.00 | 1.00 |
| eligibility x1.5 | 116 | 129 | 9 | 10 | 1.00 | 1.00 |
| recency off | 153 | 166 | 7 | 9 | 0.92 | 0.95 |
| A-team and associates at full weight | 153 | 166 | 10 | 10 | 0.99 | 0.99 |
| A-team and associate opposition removed | 145 | 159 | 10 | 10 | 0.99 | 0.99 |
| IPL only | 79 | 84 | 5 | 6 | 0.88 | 0.89 |
| T20I only | 89 | 98 | 7 | 7 | 0.83 | 0.84 |
| empirical Bayes estimator | 153 | 166 | 4 | 5 | 0.70 | 0.73 |

**Persistence** (`persistence.csv`, figure `persistence_scatter.png`). Ratings are computed separately in two halves of the matches and correlated across players eligible in both (half thresholds).

| role | split | n_common | spearman_rating | spearman_level | spearman_impact | spearman_consistency | spearman_delta | spearman_brown_rating |
|---|---|---|---|---|---|---|---|---|
| batter | season split (2022-24 vs 2025-26) | 96.00 | 0.08 | 0.08 | -0.07 | 0.05 | -0.07 | 0.15 |
| batter | odd/even match split | 145.00 | 0.06 | 0.06 | -0.01 | -0.07 | 0.01 | 0.11 |
| batter | random half splits (mean of 20) | 139.30 | 0.10 | 0.10 | -0.04 | 0.02 | 0.01 | 0.19 |
| bowler | season split (2022-24 vs 2025-26) | 104.00 | 0.18 | 0.18 | 0.04 | 0.09 | 0.03 | 0.30 |
| bowler | odd/even match split | 153.00 | 0.08 | 0.08 | 0.07 | 0.04 | -0.01 | 0.16 |
| bowler | random half splits (mean of 20) | 150.65 | 0.16 | 0.16 | 0.07 | 0.07 | -0.01 | 0.28 |

This is the most important caveat in the document. Split-half Spearman correlation of the rating is 0.10 for batters and 0.16 for bowlers (Spearman-Brown full-sample reliability 0.19 and 0.28). The Level component persists weakly; the pressure delta (0.01 and -0.01) and consistency do not persist. In plain words: who is good is measurable, who is specifically better under pressure than their own normal is mostly not, at these sample sizes. The ranking is a best estimate, not a stable ordering, and the intervals in section 1 should be taken seriously.

**Decision rule** (`decision_rule.csv`). Fixed in advance: a primary top-10 player with grid top-10 frequency below 0.40 is replaced by the best-ranked outsider at or above it.

| role | player_id | player_name | primary_rank | grid_top10_prob | action |
|---|---|---|---|---|---|
| batter |  |  |  |  | no primary top-10 player below the threshold; primary list kept |
| bowler | 4900 | Wanindu Hasaranga | 10.00 | 0.40 | below threshold, kept (no outsider at or above threshold) |

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
| Yashasvi Jaiswal | 16 | no | opener | 12 | 1.38 |  |  |  |
| Dhruv Jurel | 16 | no | middle order/finisher (5+) | 140 | -1.11 |  |  |  |
| Jofra Archer | 16 | yes | middle order/finisher (5+) |  |  | pace, powerplay-leaning | 11 | 1.76 |
| Vaibhav Sooryavanshi | 16 | no | opener | 1 | 4.23 |  |  |  |
| Donovan Ferreira | 15 | yes | middle order/finisher (5+) | 58 | 0.15 |  |  |  |
| Ravindra Jadeja | 14 | no | middle order/finisher (5+) | 117 | -0.66 | spinner | 59 | 0.26 |
| Riyan Parag | 14 | no | top/middle order (3-4) | 51 | 0.24 |  |  |  |
| Nandre Burger | 13 | yes |  |  |  | pace, powerplay-leaning | 90 | -0.09 |
| Brijesh Sharma | 13 | no |  |  |  | pace, death-leaning | 114 | -0.46 |
| Ravi Bishnoi | 9 | no |  |  |  | spinner | 153 | -1.35 |
| Shimron Hetmyer | 8 | yes | middle order/finisher (5+) | 134 | -0.93 |  |  |  |
| Yash Punja | 8 | no |  |  |  | spinner |  |  |
| Dasun Shanaka | 7 | yes | middle order/finisher (5+) | 69 | -0.08 | pace, all phases | 57 | 0.26 |
| Shubham Dubey | 7 | no | middle order/finisher (5+) |  |  |  |  |  |
| Tushar Deshpande | 7 | no |  |  |  | pace, death-leaning | 101 | -0.26 |

**Top-10 players: role, splits and gap** (`rr_fit.csv`, which also covers ranks 11 to 20 and holds the pace/spin, left/right, period and competition splits with their ball counts):

| final_rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | press_sr_vs_pace | press_sr_vs_spin | press_nrae100_2022_24 | press_nrae100_2025_26 | press_nrae100_ipl | press_nrae100_t20i | weakest_rr_regular | rating_gap_vs_weakest | displacement_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi | opener | powerplay | Rajasthan Royals | no | 255.9 | 164.7 |  | 79.8 | 112.8 | 6.7 | Yashasvi Jaiswal | 2.9 | already an RR player |
| 2 | Abhishek Sharma | opener | powerplay | Sunrisers Hyderabad | no | 195.3 | 218.0 | -3.5 | 58.6 | 8.8 | 71.9 | Yashasvi Jaiswal | 2.2 | upgrade on point estimate, inside the noise |
| 3 | Namboori Tilak Varma | middle order/finisher (5+) | middle | Mumbai Indians | no | 184.8 | 129.8 | 14.4 | 42.6 | 15.6 | 43.4 | Dhruv Jurel | 4.0 | would displace (80% intervals do not overlap) |
| 4 | Phil Salt | opener | powerplay | Royal Challengers Bengaluru | yes | 184.0 | 133.9 | 33.4 | 38.7 | 56.4 | 20.6 | Yashasvi Jaiswal | 1.4 | upgrade on point estimate, inside the noise |
| 5 | Tim David | middle order/finisher (5+) | death | Royal Challengers Bengaluru | yes | 206.1 | 128.3 | 16.9 | 75.1 | 29.8 | 33.3 | Dhruv Jurel | 3.7 | would displace (80% intervals do not overlap) |
| 6 | Ashutosh Sharma | middle order/finisher (5+) | death | Delhi Capitals | no | 197.5 | 138.7 | 24.2 | 47.9 | 41.7 |  | Dhruv Jurel | 3.1 | would displace (80% intervals do not overlap) |
| 7 | Suryakumar Yadav | top/middle order (3-4) | middle | Mumbai Indians | no | 184.4 | 135.0 | 36.9 | -10.5 | 5.2 | 46.3 | Riyan Parag | 1.7 | upgrade on point estimate, inside the noise |
| 8 | Heinrich Klaasen | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 184.4 | 182.4 | 35.2 | 39.4 | 36.8 | 36.1 | Dhruv Jurel | 3.0 | would displace (80% intervals do not overlap) |
| 9 | Pathum Nissanka | opener | powerplay | Delhi Capitals | yes | 157.2 | 146.4 | 3.2 | 48.6 | 12.6 | 30.7 | Yashasvi Jaiswal | 0.3 | upgrade on point estimate, inside the noise |
| 10 | Harry Brook | top/middle order (3-4) | middle | not in an IPL 2026 squad | yes | 185.0 | 125.0 | -13.7 | 32.5 | -99.1 | 26.2 | Riyan Parag | 1.4 | upgrade on point estimate, inside the noise |

| final_rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | press_econ_vs_rhb | press_econ_vs_lhb | press_nrae100_2022_24 | press_nrae100_2025_26 | press_nrae100_ipl | press_nrae100_t20i | weakest_rr_regular | rating_gap_vs_weakest | displacement_call |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah | pace, death-leaning | powerplay | Mumbai Indians | no | 7.5 | 6.0 | 28.1 | 38.8 | 23.1 | 71.7 | Brijesh Sharma | 4.2 | would displace (80% intervals do not overlap) |
| 2 | Varun Chakravarthy | spinner | middle | Kolkata Knight Riders | no | 7.1 | 8.5 | 34.2 | 17.4 | 12.2 | 68.0 | Ravi Bishnoi | 4.3 | would displace (80% intervals do not overlap) |
| 3 | Bhuvneshwar Kumar | pace, death-leaning | powerplay | Royal Challengers Bengaluru | no | 8.7 | 9.1 | 24.2 | 29.2 | 37.2 | -3.2 | Brijesh Sharma | 3.1 | would displace (80% intervals do not overlap) |
| 4 | Sunil Narine | spinner | middle | Kolkata Knight Riders | no | 6.4 | 7.2 | 23.8 | 19.4 | 22.3 |  | Ravi Bishnoi | 4.0 | would displace (80% intervals do not overlap) |
| 5 | Rashid Khan | spinner | middle | Gujarat Titans | yes | 7.1 | 7.9 | 38.0 | 25.5 | 31.5 | 39.3 | Ravi Bishnoi | 4.0 | would displace (80% intervals do not overlap) |
| 6 | Josh Hazlewood | pace, powerplay-leaning | powerplay | Royal Challengers Bengaluru | yes | 7.3 | 9.5 | 10.6 | 17.3 | 17.7 | 5.2 | Nandre Burger | 2.5 | would displace (80% intervals do not overlap) |
| 7 | Mohsin Khan | pace, powerplay-leaning | powerplay | Lucknow Super Giants | no | 9.5 | 6.5 | 21.4 | 141.6 | 45.3 |  | Nandre Burger | 2.1 | upgrade on point estimate, inside the noise |
| 8 | Axar Patel | spinner | middle | Delhi Capitals | no | 6.9 | 8.8 | 26.1 | 26.7 | 21.8 | 30.3 | Ravi Bishnoi | 3.3 | would displace (80% intervals do not overlap) |
| 9 | Nathan Ellis | pace, death-leaning | death | Chennai Super Kings | yes | 8.6 | 8.3 | 25.2 | 16.3 | 19.6 | 23.0 | Brijesh Sharma | 2.3 | would displace (80% intervals do not overlap) |
| 10 | Wanindu Hasaranga | spinner | middle | Lucknow Super Giants | yes | 8.3 | 8.3 | -1.0 | -9.6 | -12.8 | 5.3 | Ravi Bishnoi | 3.2 | would displace (80% intervals do not overlap) |

**Auction shortlist.** Players from the top 20 of either group who are not already at RR, whose main phase is one of RR's 2026 pressure gap cells and whose bootstrap top-10 probability is at least 0.10:

| group | rank | player_name | role | main_phase | ipl_2026_team | overseas_derived | boot_top10_prob | displacement_call | availability |
|---|---|---|---|---|---|---|---|---|---|
| batter | 3 | Namboori Tilak Varma | middle order/finisher (5+) | middle | Mumbai Indians | no | 0.75 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| batter | 7 | Suryakumar Yadav | top/middle order (3-4) | middle | Mumbai Indians | no | 0.50 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 8 | Heinrich Klaasen | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 0.44 | would displace (80% intervals do not overlap) | unknown, check after retention list |
| batter | 10 | Harry Brook | top/middle order (3-4) | middle | not in an IPL 2026 squad | yes | 0.32 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 15 | Kamindu Mendis | middle order/finisher (5+) | middle | Sunrisers Hyderabad | yes | 0.18 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 16 | Nicholas Pooran | top/middle order (3-4) | middle | Lucknow Super Giants | yes | 0.22 | upgrade on point estimate, inside the noise | unknown, check after retention list |
| batter | 17 | Shreyas Iyer | top/middle order (3-4) | middle | Punjab Kings | no | 0.17 | upgrade on point estimate, inside the noise | unknown, check after retention list |

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
- 9 of the 20 listed players finish in the top 10 in fewer than half of the bootstrap resamples: Ashutosh Sharma (0.48), Suryakumar Yadav (0.50), Heinrich Klaasen (0.44), Pathum Nissanka (0.37), Harry Brook (0.32), Mohsin Khan (0.44), Axar Patel (0.43), Nathan Ellis (0.36), Wanindu Hasaranga (0.35). The lower half of each list is close to interchangeable with ranks 11 to 25.
- The smallest pressure sample in the lists is Vaibhav Sooryavanshi with 85 pressure balls. He qualifies under the pre-registered thresholds and is kept; his interval is wide.
- The ridge and empirical Bayes estimators agree on the composite but only moderately on Level (section 5). Restricting to one competition changes the lists: top-10 overlap with the primary is IPL only, batters 5 of 10; T20I only, batters 7 of 10; IPL only, bowlers 6 of 10; T20I only, bowlers 7 of 10.
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

About 7 minutes on 4 cores for the full pipeline from the raw CSVs. Seeds are fixed in `config.json`. A run from a fresh clone reproduced every table byte for byte (DECISIONS.md, phase 2a). `python src/phase2_experiments.py` re-runs the model comparisons (about 40 minutes).

## 13. Open questions and next steps

- Check the retention lists and replace the availability column, then re-run stage 09.
- Obtain true innings totals or extras run values; the reconstruction error would vanish.
- Add leagues beyond the IPL and T20Is to raise pressure samples; persistence is limited by sample size.
- Model the pressure delta hierarchically by role (finishers, death bowlers) instead of per player; a role-level effect may be estimable where a player-level one is not.
- Use ball-tracking variables (length, line) to separate execution from outcome for bowlers.
- Test whether a win-probability model with team strength changes leverage for mismatched fixtures.

## What changed in phase 2 (before phase 3)

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

**Top-10 lists before and after** (`outputs/phase1/top10_*.csv` versus `outputs/phase2/top10_*.csv`):

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

- Abhishek Sharma: rank 3 to 2, stays in the top 10. Rating 2.42 to 2.25; the component that moved most is consistency (-0.14 rating points).
- Tim David: rank 4 to 3, stays in the top 10. Rating 1.69 to 2.01; the component that moved most is consistency (+0.15 rating points).
- Namboori Tilak Varma: rank 2 to 4, stays in the top 10. Rating 2.54 to 2.00; the component that moved most is level (-0.39 rating points).
- Phil Salt: rank 7 to 5, stays in the top 10. Rating 1.62 to 1.70; the component that moved most is consistency (+0.06 rating points).
- Sahibzada Farhan: rank 5 to 7, stays in the top 10. Rating 1.67 to 1.41; the component that moved most is level (-0.12 rating points).
- Fakhar Zaman: rank 11 to 10, enters the top 10. Rating 1.37 to 1.28; the component that moved most is level (-0.14 rating points).
- Prabhsimran Singh: rank 10 to 11, leaves the top 10. Rating 1.45 to 1.22; the component that moved most is level (-0.12 rating points).

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

- Bhuvneshwar Kumar: rank 7 to 5, stays in the top 10. Rating 1.45 to 1.82; the component that moved most is level (+0.25 rating points).
- Axar Patel: rank 5 to 6, stays in the top 10. Rating 1.63 to 1.73; the component that moved most is consistency (+0.08 rating points).
- Mohsin Khan: rank 6 to 7, stays in the top 10. Rating 1.54 to 1.46; the component that moved most is level (-0.18 rating points).
- Jason Holder: rank 11 to 10, enters the top 10. Rating 1.12 to 1.15; the component that moved most is consistency (-0.10 rating points).
- Taskin Ahmed: rank 10 to 11, leaves the top 10. Rating 1.16 to 1.09; the component that moved most is consistency (-0.06 rating points).

Every difference has the same cause, the role-aware baseline (post-hoc change P-1). It stops charging batters for the slow first balls of an innings and stops crediting bowlers for bowling to batters who have just arrived. Ratings move by up to about half a point and neighbours swap places. Ranks 9 to 12 are separated by a few hundredths of a rating point in both versions.

**Reading the scorecard honestly.** Split-half reliability swings by more than its split-to-split standard error whenever the pressure sample itself changes (compare the win-probability variants), so the standard error understates the real uncertainty of this yardstick. No variant lifts reliability to a level that would change the main caveat of this document: the rating is a noisy best estimate. One change was adopted, the role-aware baseline, because it makes the baseline measurably more accurate and removes a bias against batters who face many first balls. Everything else in the pre-registered specification is unchanged.

## What changed in phase 3

Phase 3 looked for the best rating the supplied data can support. The yardstick was made stricter than phase 2's: rate players from one random half of the matches and measure how well that rating predicts the same players' raw pressure performance in the other half (weighted Spearman correlation, weights = held-out pressure balls), over 20 random splits in both directions, for two targets (pressure NRAE and pressure WPA per 100 balls). Rating-versus-rating correlation, used in phase 2, can reward a score for being stable noise; this cannot. Differences are paired: every candidate is scored on the same splits. A 2022-24 to 2025-26 temporal test was kept apart from the selection and used only to confirm. Rule fixed before adopting: the highest sum of the four random-split correlations wins, provided it does not lose to the old composite on the temporal NRAE check. Name and identity of players played no part.

**Finding 1. The extra components did not predict anything.** Single components used alone (`phase3_candidates.csv`, mean over splits, pressure NRAE target):

| candidate | batters | bowlers |
|---|---|---|
| consistency only | -0.005 | 0.087 |
| delta only | 0.035 | 0.090 |
| impact only | -0.037 | 0.084 |
| level only | 0.051 | 0.129 |
| level only [leverage-weighted (alpha 1)] | 0.060 | 0.139 |
| primary composite | 0.035 | 0.115 |

Level predicts held-out pressure performance. Delta and consistency are at or near zero, and impact is negative for batters. The specification gave these three 60% of the weight; they added noise.

**Finding 2. Weighting each ball by its leverage is a better 'pressure level' than a cutoff.** Candidates, paired against the old composite on the same splits (`phase3_final_candidates.csv`; positive = better):

| role | candidate | pred_nrae | pred_wpa | d_nrae_vs_spec | d_nrae_se | d_wpa_vs_spec | d_wpa_se |
|---|---|---|---|---|---|---|---|
| bat | spec composite (phase 1-2) | 0.035 | 0.014 | 0.000 | 0.000 | 0.000 | 0.000 |
| bat | level (unweighted) | 0.051 | 0.003 | 0.016 | 0.008 | -0.012 | 0.007 |
| bat | lev-level a=1 | 0.060 | 0.034 | 0.025 | 0.008 | 0.019 | 0.007 |
| bat | lev-level a=2 | 0.043 | 0.030 | 0.008 | 0.010 | 0.016 | 0.011 |
| bat | lev 0.8L 0.2I a=1 | 0.053 | 0.035 | 0.018 | 0.008 | 0.020 | 0.007 |
| bat | lev 0.7L 0.3I a=1 | 0.048 | 0.034 | 0.014 | 0.008 | 0.019 | 0.007 |
| bat | lev 0.6L 0.25I 0.15D a=1 | 0.049 | 0.035 | 0.014 | 0.007 | 0.021 | 0.006 |
| bat | lev spec weights a=1 | 0.032 | 0.033 | -0.002 | 0.005 | 0.018 | 0.005 |
| bat | lev 0.7L 0.3I a=2 | 0.023 | 0.026 | -0.012 | 0.010 | 0.012 | 0.011 |
| bowl | spec composite (phase 1-2) | 0.115 | 0.121 | 0.000 | 0.000 | 0.000 | 0.000 |
| bowl | level (unweighted) | 0.129 | 0.105 | 0.014 | 0.007 | -0.016 | 0.006 |
| bowl | lev-level a=1 | 0.139 | 0.117 | 0.024 | 0.007 | -0.003 | 0.006 |
| bowl | lev-level a=2 | 0.120 | 0.098 | 0.005 | 0.012 | -0.023 | 0.011 |
| bowl | lev 0.8L 0.2I a=1 | 0.131 | 0.122 | 0.016 | 0.007 | 0.002 | 0.006 |
| bowl | lev 0.7L 0.3I a=1 | 0.125 | 0.124 | 0.010 | 0.007 | 0.003 | 0.006 |
| bowl | lev 0.6L 0.25I 0.15D a=1 | 0.120 | 0.119 | 0.005 | 0.007 | -0.001 | 0.006 |
| bowl | lev spec weights a=1 | 0.117 | 0.120 | 0.002 | 0.006 | -0.001 | 0.006 |
| bowl | lev 0.7L 0.3I a=2 | 0.111 | 0.105 | -0.003 | 0.012 | -0.015 | 0.011 |

Temporal confirmation, rated on 2022-24 and scored on 2025-26 pressure performance (`phase3_temporal.csv`; one draw, so no standard error):

| role | candidate | pred_nrae_2025_26 | pred_wpa_2025_26 |
|---|---|---|---|
| bat | spec composite (phase 1-2) | 0.111 | -0.042 |
| bat | level (unweighted) | 0.174 | 0.079 |
| bat | lev-level a=1 | 0.128 | 0.010 |
| bat | lev-level a=2 | 0.052 | -0.095 |
| bat | lev 0.8L 0.2I a=1 | 0.112 | -0.016 |
| bat | lev 0.7L 0.3I a=1 | 0.096 | -0.033 |
| bat | lev 0.6L 0.25I 0.15D a=1 | 0.078 | -0.053 |
| bat | lev spec weights a=1 | 0.079 | -0.047 |
| bat | lev 0.7L 0.3I a=2 | 0.018 | -0.130 |
| bowl | spec composite (phase 1-2) | 0.255 | 0.377 |
| bowl | level (unweighted) | 0.319 | 0.424 |
| bowl | lev-level a=1 | 0.308 | 0.310 |
| bowl | lev-level a=2 | 0.292 | 0.238 |
| bowl | lev 0.8L 0.2I a=1 | 0.291 | 0.291 |
| bowl | lev 0.7L 0.3I a=1 | 0.276 | 0.273 |
| bowl | lev 0.6L 0.25I 0.15D a=1 | 0.274 | 0.269 |
| bowl | lev spec weights a=1 | 0.248 | 0.254 |
| bowl | lev 0.7L 0.3I a=2 | 0.260 | 0.184 |

**Reading it honestly.** On the random splits the leverage-weighted level beats the old composite on both targets for batters (about 3 standard errors on WPA) and on NRAE for bowlers (about 3.5). On the temporal test it beats the old composite on NRAE in both groups, but the plain unweighted level scores higher still for batters, and the old composite scores higher on WPA for bowlers. The temporal draw is a single sample of about 100 players and is noisy; it shows the improvement is not purely an artefact of random splits, not that this exact variant is the optimum. The absolute correlations are small (batters about 0.06, bowlers about 0.14): pressure performance is only weakly predictable from past pressure performance, so every ranking here, old or new, is a noisy estimate.

**Adopted (post-hoc change P-2).** The rating is the leverage-weighted level (weight = leverage, power 1) with eligibility, opponent adjustment and all other parts unchanged. Impact, consistency and delta stay in the tables as descriptive columns and as sensitivity configurations. The pre-registered composite is kept as the `spec weights` configuration in the sensitivity grid and in `outputs/phase2/`.

How much the lists depend on this choice (`sensitivity_configs.csv`, top-10 overlap with the final lists):

| role | config | n_eligible | top10_overlap_with_primary | spearman_with_primary |
|---|---|---|---|---|
| batter | no leverage weighting | 153 | 6 | 0.80 |
| batter | leverage weight power 0.5 | 153 | 8 | 0.95 |
| batter | leverage weight power 2 | 153 | 6 | 0.84 |
| batter | spec weights 0.40/0.25/0.20/0.15 | 153 | 10 | 0.83 |
| bowler | no leverage weighting | 166 | 6 | 0.88 |
| bowler | leverage weight power 0.5 | 166 | 8 | 0.97 |
| bowler | leverage weight power 2 | 166 | 9 | 0.82 |
| bowler | spec weights 0.40/0.25/0.20/0.15 | 166 | 10 | 0.86 |

**Other phase 3 attempts that did not help.** Averaging the win-probability models gave log loss 0.5217 against 0.5220, which is nothing; the win-probability model is at its ceiling for these features and was not changed. Leverage power 2 predicts worse than power 1 (it concentrates weight on too few balls). Re-tuning the ridge penalties under leverage weighting moved them to 3,000 and 30,000 and left the conclusions unchanged (the table above was recomputed with them).

**Persistence after phase 3** (`persistence.csv`). Split-half reliability of the rating rose from 0.06 to 0.10 for batters and from 0.12 to 0.16 for bowlers. Still low; see section 8.

**Top-10 lists before and after** (`outputs/phase2/top10_*.csv` versus `outputs/tables/top10_*.csv`):

*Batters*

| Rank | Phase 2 | Phase 3 (final) |
|---|---|---|
| 1 | Vaibhav Sooryavanshi | Vaibhav Sooryavanshi |
| 2 | Abhishek Sharma | Abhishek Sharma |
| 3 | Tim David | Namboori Tilak Varma |
| 4 | Namboori Tilak Varma | Phil Salt |
| 5 | Phil Salt | Tim David |
| 6 | Heinrich Klaasen | Ashutosh Sharma |
| 7 | Sahibzada Farhan | Suryakumar Yadav |
| 8 | Pathum Nissanka | Heinrich Klaasen |
| 9 | Shreyas Iyer | Pathum Nissanka |
| 10 | Fakhar Zaman | Harry Brook |

- Namboori Tilak Varma: rank 4 to 3, stays in the top 10. Level z +0.82 (unweighted) to +2.87 (leverage-weighted); the three dropped components had contributed +1.67 to the old rating (impact +2.4, consistency +1.7, delta +4.8).
- Phil Salt: rank 5 to 4, stays in the top 10. Level z +2.31 (unweighted) to +2.74 (leverage-weighted); the three dropped components had contributed +0.77 to the old rating (impact +0.5, consistency +2.1, delta +1.4).
- Tim David: rank 3 to 5, stays in the top 10. Level z +2.88 (unweighted) to +2.62 (leverage-weighted); the three dropped components had contributed +0.86 to the old rating (impact +1.1, consistency +1.9, delta +1.5).
- Ashutosh Sharma: rank 20 to 6, enters the top 10. Level z +0.80 (unweighted) to +2.02 (leverage-weighted); the three dropped components had contributed +0.51 to the old rating (impact +1.0, consistency +0.1, delta +1.5).
- Suryakumar Yadav: rank 19 to 7, enters the top 10. Level z +2.20 (unweighted) to +1.99 (leverage-weighted); the three dropped components had contributed -0.04 to the old rating (impact -0.6, consistency +0.3, delta +0.3).
- Heinrich Klaasen: rank 6 to 8, stays in the top 10. Level z +1.97 (unweighted) to +1.92 (leverage-weighted); the three dropped components had contributed +0.75 to the old rating (impact +1.1, consistency +1.3, delta +1.4).
- Pathum Nissanka: rank 8 to 9, stays in the top 10. Level z +1.52 (unweighted) to +1.72 (leverage-weighted); the three dropped components had contributed +0.74 to the old rating (impact +0.7, consistency +1.6, delta +1.7).
- Harry Brook: rank 43 to 10, enters the top 10. Level z +0.94 (unweighted) to +1.62 (leverage-weighted); the three dropped components had contributed -0.08 to the old rating (impact +0.2, consistency -0.6, delta -0.1).
- Sahibzada Farhan: rank 7 to 14, leaves the top 10. Level z +1.39 (unweighted) to +1.28 (leverage-weighted); the three dropped components had contributed +0.85 to the old rating (impact +1.5, consistency +1.3, delta +1.4).
- Shreyas Iyer: rank 9 to 17, leaves the top 10. Level z +0.50 (unweighted) to +1.08 (leverage-weighted); the three dropped components had contributed +1.13 to the old rating (impact +2.2, consistency +1.7, delta +1.7).
- Fakhar Zaman: rank 10 to 30, leaves the top 10. Level z -0.10 (unweighted) to +0.82 (leverage-weighted); the three dropped components had contributed +1.32 to the old rating (impact +2.0, consistency +2.5, delta +2.1).

*Bowlers*

| Rank | Phase 2 | Phase 3 (final) |
|---|---|---|
| 1 | Jasprit Bumrah | Jasprit Bumrah |
| 2 | Varun Chakravarthy | Varun Chakravarthy |
| 3 | Sunil Narine | Bhuvneshwar Kumar |
| 4 | Rashid Khan | Sunil Narine |
| 5 | Bhuvneshwar Kumar | Rashid Khan |
| 6 | Axar Patel | Josh Hazlewood |
| 7 | Mohsin Khan | Mohsin Khan |
| 8 | Nathan Ellis | Axar Patel |
| 9 | Josh Hazlewood | Nathan Ellis |
| 10 | Jason Holder | Wanindu Hasaranga |

- Bhuvneshwar Kumar: rank 5 to 3, stays in the top 10. Level z +2.62 (unweighted) to +2.68 (leverage-weighted); the three dropped components had contributed +0.78 to the old rating (impact +0.8, consistency +1.1, delta +2.3).
- Sunil Narine: rank 3 to 4, stays in the top 10. Level z +2.49 (unweighted) to +2.67 (leverage-weighted); the three dropped components had contributed +1.21 to the old rating (impact +2.3, consistency +2.2, delta +1.3).
- Rashid Khan: rank 4 to 5, stays in the top 10. Level z +1.91 (unweighted) to +2.66 (leverage-weighted); the three dropped components had contributed +1.33 to the old rating (impact +2.1, consistency +2.0, delta +2.7).
- Josh Hazlewood: rank 9 to 6, stays in the top 10. Level z +2.23 (unweighted) to +2.38 (leverage-weighted); the three dropped components had contributed +0.45 to the old rating (impact +1.6, consistency +0.0, delta +0.3).
- Axar Patel: rank 6 to 8, stays in the top 10. Level z +0.60 (unweighted) to +1.97 (leverage-weighted); the three dropped components had contributed +1.49 to the old rating (impact +1.6, consistency +2.2, delta +4.4).
- Nathan Ellis: rank 8 to 9, stays in the top 10. Level z +1.69 (unweighted) to +1.86 (leverage-weighted); the three dropped components had contributed +0.68 to the old rating (impact +1.1, consistency +0.8, delta +1.6).
- Wanindu Hasaranga: rank 50 to 10, enters the top 10. Level z +1.62 (unweighted) to +1.83 (leverage-weighted); the three dropped components had contributed -0.38 to the old rating (impact +0.2, consistency -1.7, delta -0.6).
- Jason Holder: rank 10 to 15, leaves the top 10. Level z +2.22 (unweighted) to +1.28 (leverage-weighted); the three dropped components had contributed +0.26 to the old rating (impact +0.2, consistency +1.1, delta -0.0).

The lists change because the rating changed definition: players whose pressure results came with good impact or consistency numbers but a modest underlying level move down, and players with a high leverage-weighted level move up. Ranks 6 to 12 are separated by a fraction of a rating point in both versions and are close to interchangeable.

## Exact dropdown selections

**Batters**

1. Vaibhav Sooryavanshi (50284)
2. Abhishek Sharma (6281)
3. Namboori Tilak Varma (7897)
4. Phil Salt (5553)
5. Tim David (6396)
6. Ashutosh Sharma (8101)
7. Suryakumar Yadav (1699)
8. Heinrich Klaasen (4260)
9. Pathum Nissanka (6931)
10. Harry Brook (6280)

**Bowlers**

1. Jasprit Bumrah (2933)
2. Varun Chakravarthy (6256)
3. Bhuvneshwar Kumar (360)
4. Sunil Narine (781)
5. Rashid Khan (4722)
6. Josh Hazlewood (830)
7. Mohsin Khan (6669)
8. Axar Patel (2876)
9. Nathan Ellis (7920)
10. Wanindu Hasaranga (4900)
