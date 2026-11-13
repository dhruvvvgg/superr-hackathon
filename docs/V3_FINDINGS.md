# Final model (V3): who delivers under pressure

This is the recommended candidate model. It extends V2 with a batter pace interaction and stronger shrinkage of the bowler wicket component. Candidate adoption is based on tuning trials only (paired z > 2). The legacy confirmation trials are descriptive diagnostics, not an untouched holdout: earlier V3 iterations used them for candidate gating. All tables are in outputs/v3/.

**Rebuild required:** the numeric tables below are the previously committed V3 outputs, not results from the revised chronological pipeline on this branch. Run `python run_all.py` to regenerate the model-selection tables, temporal validation, V3 ratings, RR fit, anomaly audits and acceptance tests. Re-check the tuning-only evidence before treating the existing chosen configuration as confirmed under the revised upstream folds.

## 1. Result

Rating: leverage-weighted, opponent-adjusted NRAE per 100 balls, shrunk toward average for small samples. It estimates overall performance on high-leverage deliveries relative to an identity-free expected-value baseline. It is not a causal estimate of within-player pressure uplift and it is not a consistency score. Raw pressure-versus-normal strike-rate/economy contrasts and pressure-innings dispersion are descriptive diagnostics, not ranking inputs. The interval is the 80% interval over 1,000 match resamples.

### Top 10 batters (`outputs/v3/top10_batters.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) | Pressure balls |
|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi (50284) | 22.15 | 11.9 to 31.5 | 1 to 6 | 0.94 | 85 |
| 2 | Abhishek Sharma (6281) | 14.69 | 7.0 to 22.1 | 1 to 23 | 0.78 | 300 |
| 3 | Namboori Tilak Varma (7897) | 13.65 | 7.3 to 19.5 | 2 to 20 | 0.77 | 514 |
| 4 | Phil Salt (5553) | 12.86 | 7.1 to 17.7 | 2 to 21 | 0.72 | 200 |
| 5 | Tim David (6396) | 11.25 | 6.0 to 16.8 | 3 to 28 | 0.62 | 321 |
| 6 | Ashutosh Sharma (8101) | 10.81 | 3.8 to 18.3 | 2 to 44 | 0.54 | 112 |
| 7 | Harry Brook (6280) | 10.04 | 3.7 to 16.5 | 3 to 45 | 0.47 | 140 |
| 8 | Suryakumar Yadav (1699) | 8.92 | 3.8 to 13.9 | 4 to 44 | 0.38 | 478 |
| 9 | Pathum Nissanka (6931) | 8.57 | 3.2 to 13.7 | 4 to 49 | 0.35 | 263 |
| 10 | Heinrich Klaasen (4260) | 8.03 | 4.3 to 11.4 | 7 to 40 | 0.23 | 256 |

1. **Vaibhav Sooryavanshi**: +20.9 from scoring and +1.2 from not getting out (per 100 balls); strike rate 238 under pressure against 220 otherwise, 202 runs and 4 dismissals in 85 pressure balls.
2. **Abhishek Sharma**: +19.4 from scoring and -4.7 from not getting out (per 100 balls); strike rate 202 under pressure against 185 otherwise, 606 runs and 18 dismissals in 300 pressure balls.
3. **Namboori Tilak Varma**: +3.1 from scoring and +10.5 from not getting out (per 100 balls); strike rate 167 under pressure against 137 otherwise, 856 runs and 20 dismissals in 514 pressure balls.
4. **Phil Salt**: +9.0 from scoring and +3.9 from not getting out (per 100 balls); strike rate 170 under pressure against 171 otherwise, 340 runs and 7 dismissals in 200 pressure balls.
5. **Tim David**: +10.2 from scoring and +1.1 from not getting out (per 100 balls); strike rate 192 under pressure against 172 otherwise, 615 runs and 23 dismissals in 321 pressure balls.
6. **Ashutosh Sharma**: +6.5 from scoring and +4.3 from not getting out (per 100 balls); strike rate 181 under pressure against 160 otherwise, 203 runs and 7 dismissals in 112 pressure balls.
7. **Harry Brook**: +8.7 from scoring and +1.3 from not getting out (per 100 balls); strike rate 159 under pressure against 166 otherwise, 223 runs and 10 dismissals in 140 pressure balls.
8. **Suryakumar Yadav**: +7.5 from scoring and +1.4 from not getting out (per 100 balls); strike rate 168 under pressure against 167 otherwise, 804 runs and 24 dismissals in 478 pressure balls.
9. **Pathum Nissanka**: +4.2 from scoring and +4.4 from not getting out (per 100 balls); strike rate 153 under pressure against 133 otherwise, 403 runs and 13 dismissals in 263 pressure balls.
10. **Heinrich Klaasen**: +3.2 from scoring and +4.8 from not getting out (per 100 balls); strike rate 184 under pressure against 163 otherwise, 470 runs and 14 dismissals in 256 pressure balls.

Figure: `outputs/v3/v3_top10_batters.png`.

### Top 10 bowlers (`outputs/v3/top10_bowlers.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) | Pressure balls |
|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah (2933) | 13.52 | 10.3 to 16.7 | 1 to 2 | 1.00 | 366 |
| 2 | Sunil Narine (781) | 9.17 | 6.7 to 11.8 | 2 to 7 | 0.98 | 351 |
| 3 | Rashid Khan (4722) | 9.08 | 6.9 to 11.5 | 2 to 6 | 0.98 | 484 |
| 4 | Bhuvneshwar Kumar (360) | 8.07 | 4.9 to 10.8 | 2 to 12 | 0.88 | 560 |
| 5 | Josh Hazlewood (830) | 7.36 | 4.4 to 10.3 | 2 to 15 | 0.83 | 333 |
| 6 | Varun Chakravarthy (6256) | 5.95 | 3.1 to 9.0 | 3 to 28 | 0.64 | 401 |
| 7 | Nathan Ellis (7920) | 5.48 | 3.4 to 7.6 | 5 to 24 | 0.55 | 247 |
| 8 | Axar Patel (2876) | 4.83 | 2.4 to 7.3 | 5 to 39 | 0.42 | 446 |
| 9 | Mohsin Khan (6669) | 4.76 | 1.9 to 7.6 | 5 to 48 | 0.41 | 151 |
| 10 | Matheesha Pathirana (8661) | 4.34 | 1.9 to 6.7 | 6 to 47 | 0.33 | 241 |

1. **Jasprit Bumrah**: +13.9 from runs saved and -0.4 from wickets (per 100 balls); economy 7.07 under pressure against 7.15 otherwise, 20 wickets in 366 pressure balls.
2. **Sunil Narine**: +9.3 from runs saved and -0.2 from wickets (per 100 balls); economy 6.74 under pressure against 6.80 otherwise, 14 wickets in 351 pressure balls.
3. **Rashid Khan**: +8.9 from runs saved and +0.2 from wickets (per 100 balls); economy 7.40 under pressure against 7.40 otherwise, 41 wickets in 484 pressure balls.
4. **Bhuvneshwar Kumar**: +7.8 from runs saved and +0.3 from wickets (per 100 balls); economy 8.87 under pressure against 8.04 otherwise, 39 wickets in 560 pressure balls.
5. **Josh Hazlewood**: +7.0 from runs saved and +0.4 from wickets (per 100 balls); economy 8.17 under pressure against 8.29 otherwise, 24 wickets in 333 pressure balls.
6. **Varun Chakravarthy**: +5.2 from runs saved and +0.8 from wickets (per 100 balls); economy 7.59 under pressure against 8.16 otherwise, 25 wickets in 401 pressure balls.
7. **Nathan Ellis**: +5.4 from runs saved and +0.1 from wickets (per 100 balls); economy 8.49 under pressure against 8.06 otherwise, 16 wickets in 247 pressure balls.
8. **Axar Patel**: +4.6 from runs saved and +0.2 from wickets (per 100 balls); economy 7.38 under pressure against 7.97 otherwise, 24 wickets in 446 pressure balls.
9. **Mohsin Khan**: +4.5 from runs saved and +0.2 from wickets (per 100 balls); economy 8.41 under pressure against 8.51 otherwise, 11 wickets in 151 pressure balls.
10. **Matheesha Pathirana**: +4.2 from runs saved and +0.1 from wickets (per 100 balls); economy 8.82 under pressure against 8.60 otherwise, 22 wickets in 241 pressure balls.

Figure: `outputs/v3/v3_top10_bowlers.png`.

## 2. Predictive comparison with V2 (legacy confirmation is descriptive only)

| role | trials | v3 | v2 | gain | gain_se | gain_z | n_trials |
|---|---|---|---|---|---|---|---|
| batters | tuning trials | 0.0582 | 0.0434 | 0.0148 | 0.0043 | 3.3982 | 25 |
| batters | confirmation trials | 0.0738 | 0.0651 | 0.0087 | 0.0043 | 2.0408 | 22 |
| bowlers | tuning trials | 0.1640 | 0.1417 | 0.0223 | 0.0104 | 2.1515 | 25 |
| bowlers | confirmation trials | 0.2156 | 0.1888 | 0.0268 | 0.0091 | 2.9498 | 22 |

For comparison on the confirmation trials, raw pressure strike rate scores 0.028 for batters and raw pressure economy 0.088 for bowlers. Figure: `outputs/v3/v3_confirmation.png`.

## 3. What changed from V2, and the evidence

1. **Bowlers: the wicket part of the rating is shrunk ten times harder than the runs part.** Wickets under pressure are rare and noisy; run prevention is far more repeatable. Giving each its own shrinkage lets the rating keep the repeatable part.
2. **Batters: a shrunk pace-versus-spin adjustment.** Each batter gets a small, heavily shrunk extra effect against pace, applied in proportion to how much pace he faces.
3. **Batters: a richer situational baseline.** Expected runs and dismissal also know recent momentum, the dot-ball streak, live win probability, ball position in the over, partnership length and the bowler's workload. Same features did not help bowlers (worse on confirmation), so the bowler baseline is unchanged.

Chosen configuration (`outputs/v3/chosen_config.json`):

| group | half_life | alpha | assoc_w | lam | opp_adjust | inter | lam_inter | credit | lam_wkt |
|---|---|---|---|---|---|---|---|---|---|
| bat | 24.00 | 1.00 | 0.50 | 3000.00 | yes | pace | 3000.00 | bat_credit_v3 |  |
| bowl |  | 1.00 | 1.00 | 3000.00 | yes |  |  | bowl_credit | 30000.00 |

### Every variant tried (paired difference against the current base; adoption uses tuning z > 2 only)

**Round 1, structure** (`structure.csv`, base = V2):

| role | candidate | tune_diff | tune_z | conf_diff | conf_z | passes |
|---|---|---|---|---|---|---|
| bat | base | 0.000 | 0.000 | 0.000 | 0.000 | no |
| bat | floor 0.15 | -0.000 | -0.634 | -0.000 | -0.459 | no |
| bat | floor 0.3 | -0.002 | -1.728 | -0.002 | -1.649 | no |
| bat | floor 0.5 | -0.004 | -1.444 | -0.002 | -0.615 | no |
| bat | lam_wkt x0.3 | -0.009 | -0.880 | -0.016 | -2.612 | no |
| bat | lam_wkt x3 | -0.008 | -1.043 | 0.003 | 0.350 | no |
| bat | lam_wkt x10 | -0.010 | -0.981 | -0.004 | -0.319 | no |
| bat | lam_wkt x30 | -0.012 | -1.027 | -0.006 | -0.411 | no |
| bat | lam_opp x0.3 | 0.000 | 0.379 | -0.001 | -0.710 | no |
| bat | lam_opp x3 | 0.001 | 0.772 | -0.000 | -0.089 | no |
| bat | inter pace lam 3000 | 0.009 | 2.214 | 0.006 | 1.505 | yes |
| bat | inter death lam 3000 | 0.001 | 0.364 | 0.003 | 1.438 | no |
| bat | inter pace lam 10000 | 0.004 | 1.773 | 0.003 | 1.768 | no |
| bat | inter death lam 10000 | 0.001 | 0.403 | 0.001 | 0.696 | no |
| bat | inter pace lam 30000 | 0.002 | 2.005 | 0.001 | 1.511 | yes |
| bat | inter death lam 30000 | 0.000 | 0.008 | 0.000 | 0.258 | no |
| bat | cap 3 | 0.006 | 1.550 | 0.008 | 3.048 | no |
| bat | cap 30 | 0.002 | 1.178 | 0.002 | 1.400 | no |
| bat | alpha 0.5 | -0.008 | -1.401 | -0.008 | -1.718 | no |
| bat | alpha 1.5 | -0.000 | -0.062 | -0.006 | -0.937 | no |
| bat | alpha 0 | -0.021 | -1.613 | -0.028 | -2.385 | no |
| bat | half-life x0.5 | -0.002 | -0.427 | -0.018 | -2.865 | no |
| bat | half-life x2 | -0.004 | -1.196 | 0.005 | 1.422 | no |
| bat | ens alpha 0.5/1/1.5 | -0.002 | -2.318 | -0.004 | -4.076 | no |
| bat | ens alpha 0/1 | -0.007 | -1.359 | -0.013 | -2.352 | no |
| bat | ens half-lives | -0.000 | -0.582 | -0.003 | -1.780 | no |
| bat | ens alpha x half-life | -0.001 | -0.723 | -0.004 | -4.509 | no |
| bowl | base | 0.000 | 0.000 | 0.000 | 0.000 | no |
| bowl | floor 0.15 | -0.000 | -0.551 | -0.001 | -2.307 | no |
| bowl | floor 0.3 | -0.002 | -2.646 | -0.005 | -3.549 | no |
| bowl | floor 0.5 | -0.005 | -2.639 | -0.006 | -3.348 | no |
| bowl | lam_wkt x0.3 | -0.045 | -4.155 | -0.053 | -8.357 | no |
| bowl | lam_wkt x3 | 0.015 | 2.076 | 0.022 | 4.152 | yes |
| bowl | lam_wkt x10 | 0.022 | 2.108 | 0.027 | 2.882 | yes |
| bowl | lam_wkt x30 | 0.022 | 1.771 | 0.025 | 2.430 | no |
| bowl | lam_opp x0.3 | -0.000 | -0.436 | -0.002 | -1.917 | no |
| bowl | lam_opp x3 | -0.000 | -0.053 | 0.000 | 0.446 | no |
| bowl | inter lhb lam 3000 | -0.003 | -0.892 | -0.002 | -0.926 | no |
| bowl | inter death lam 3000 | 0.001 | 0.155 | 0.001 | 0.311 | no |
| bowl | inter lhb lam 10000 | -0.000 | -0.116 | 0.000 | 0.324 | no |
| bowl | inter death lam 10000 | -0.000 | -0.142 | 0.000 | 0.266 | no |
| bowl | inter lhb lam 30000 | -0.001 | -1.483 | 0.000 | 0.001 | no |
| bowl | inter death lam 30000 | -0.000 | -0.126 | 0.001 | 1.048 | no |
| bowl | cap 3 | -0.000 | -0.096 | -0.002 | -0.693 | no |
| bowl | cap 30 | -0.000 | -0.104 | -0.002 | -1.343 | no |
| bowl | alpha 0.5 | -0.012 | -2.277 | -0.003 | -0.642 | no |
| bowl | alpha 1.5 | 0.005 | 0.876 | -0.008 | -1.426 | no |
| bowl | alpha 0 | -0.039 | -3.614 | -0.020 | -1.918 | no |
| bowl | half-life 48 | -0.012 | -3.051 | -0.019 | -4.716 | no |
| bowl | half-life 24 | -0.024 | -3.616 | -0.033 | -4.490 | no |
| bowl | ens alpha 0.5/1/1.5 | -0.001 | -0.618 | -0.000 | -0.481 | no |
| bowl | ens alpha 0/1 | -0.015 | -3.177 | -0.004 | -0.781 | no |
| bowl | ens half-lives | -0.011 | -3.015 | -0.018 | -4.799 | no |
| bowl | ens alpha x half-life | -0.007 | -2.666 | -0.011 | -4.548 | no |

**Round 2, combinations on the round-1 winners** (`combine.csv`):

| role | candidate | tune_diff | tune_z | conf_diff | conf_z | passes |
|---|---|---|---|---|---|---|
| bat | v2 base | -0.009 | -2.214 | -0.006 | -1.505 | no |
| bat | base | 0.000 | 0.000 | 0.000 | 0.000 | no |
| bat | inter pace lam 1000 | -0.001 | -0.231 | -0.002 | -0.500 | no |
| bat | inter pace lam 2000 | -0.000 | -0.035 | -0.001 | -0.395 | no |
| bat | inter pace lam 5000 | -0.002 | -1.379 | -0.002 | -1.402 | no |
| bat | + cap 3 | 0.005 | 1.154 | 0.008 | 2.753 | no |
| bat | + cap 5 | 0.000 | 0.229 | 0.001 | 0.390 | no |
| bat | + lam_wkt x3 | -0.001 | -0.298 | 0.010 | 2.022 | no |
| bat | + half-life 48 | -0.005 | -1.210 | 0.010 | 2.710 | no |
| bat | + lam x0.5 | -0.001 | -0.682 | -0.004 | -2.922 | no |
| bat | + lam x2 | -0.001 | -0.429 | -0.001 | -0.738 | no |
| bowl | v2 base | -0.022 | -2.108 | -0.027 | -2.882 | no |
| bowl | base | 0.000 | 0.000 | 0.000 | 0.000 | no |
| bowl | lam_wkt x5 | -0.004 | -2.044 | -0.002 | -0.949 | no |
| bowl | lam_wkt x20 | -0.001 | -0.544 | -0.001 | -0.618 | no |
| bowl | + alpha 1.5 | 0.009 | 1.477 | -0.001 | -0.254 | no |
| bowl | + alpha 0.5 | -0.018 | -2.609 | -0.016 | -3.471 | no |
| bowl | + cap 3 | -0.007 | -2.093 | -0.006 | -1.631 | no |
| bowl | + inter death 10000 | -0.002 | -1.116 | 0.002 | 1.190 | no |
| bowl | + inter lhb 10000 | -0.002 | -1.740 | 0.000 | 0.169 | no |
| bowl | + lam x0.5 | 0.001 | 1.047 | 0.002 | 1.715 | no |
| bowl | + lam x2 | -0.002 | -1.538 | -0.005 | -4.008 | no |
| bowl | + half-life 72 | -0.005 | -1.904 | -0.011 | -3.015 | no |

**Round 3, how the score is formed** (`score.csv`, richer-baseline credit for batters is in `score_xfeat.csv`):

| role | candidate | tune_diff | tune_z | conf_diff | conf_z | passes |
|---|---|---|---|---|---|---|
| bat | base | 0.000 | 0.000 | 0.000 | 0.000 | no |
| bat | wicket part x0.5 | -0.006 | -0.948 | 0.008 | 1.309 | no |
| bat | wicket part x0.75 | -0.001 | -0.380 | 0.005 | 1.600 | no |
| bat | wicket part x1.25 | -0.006 | -1.382 | -0.009 | -1.724 | no |
| bat | wicket part x1.5 | -0.012 | -1.705 | -0.013 | -2.191 | no |
| bat | + WPA blend 0.1 | -0.005 | -2.530 | -0.004 | -1.229 | no |
| bat | + WPA blend 0.25 | -0.007 | -1.756 | -0.004 | -1.137 | no |
| bat | + WPA blend 0.5 | -0.011 | -1.889 | -0.008 | -1.506 | no |
| bowl | base | 0.000 | 0.000 | 0.000 | 0.000 | no |
| bowl | wicket part x0.5 | -0.001 | -0.597 | -0.001 | -0.605 | no |
| bowl | wicket part x0.75 | -0.001 | -0.881 | 0.000 | 0.305 | no |
| bowl | wicket part x1.25 | -0.001 | -1.399 | -0.001 | -0.684 | no |
| bowl | wicket part x1.5 | -0.002 | -1.638 | -0.001 | -0.633 | no |
| bowl | + WPA blend 0.1 | -0.000 | -0.202 | -0.001 | -1.051 | no |
| bowl | + WPA blend 0.25 | 0.001 | 0.157 | -0.001 | -0.585 | no |
| bowl | + WPA blend 0.5 | -0.001 | -0.135 | -0.005 | -1.101 | no |

**Richer baseline, same model on both credit tables** (`_trials_baseonly_*.csv`):

| role | trials | richer_baseline_gain | se |
|---|---|---|---|
| bat | tune | 0.0063 | 0.0019 |
| bat | conf | 0.0023 | 0.0019 |
| bowl | tune | 0.0012 | 0.0023 |
| bowl | conf | -0.0032 | 0.0018 |

**Tried and rejected in this phase:** ensembles of configurations (all worse), leverage floors and caps, separate opponent penalties, death-overs and left-hander interaction terms, re-weighting the wicket part of the score, and blending in win-probability impact. A leverage cap of 3 for batters came close (positive on both trial sets, tuning z about 1.2 to 1.5) and was not adopted under the rule.

## 4. How the final lists compare

- Batters: 10 of 10 shared with V2, 10 of 10 with phase 3. In against V2: none; out: none.

| Rank | V2 | Final (V3) |
|---|---|---|
| 1 | Vaibhav Sooryavanshi | Vaibhav Sooryavanshi |
| 2 | Abhishek Sharma | Abhishek Sharma |
| 3 | Phil Salt | Namboori Tilak Varma |
| 4 | Namboori Tilak Varma | Phil Salt |
| 5 | Tim David | Tim David |
| 6 | Suryakumar Yadav | Ashutosh Sharma |
| 7 | Heinrich Klaasen | Harry Brook |
| 8 | Ashutosh Sharma | Suryakumar Yadav |
| 9 | Pathum Nissanka | Pathum Nissanka |
| 10 | Harry Brook | Heinrich Klaasen |

- Bowlers: 9 of 10 shared with V2, 9 of 10 with phase 3. In against V2: Matheesha Pathirana; out: Lockie Ferguson.

| Rank | V2 | Final (V3) |
|---|---|---|
| 1 | Jasprit Bumrah | Jasprit Bumrah |
| 2 | Varun Chakravarthy | Sunil Narine |
| 3 | Bhuvneshwar Kumar | Rashid Khan |
| 4 | Josh Hazlewood | Bhuvneshwar Kumar |
| 5 | Rashid Khan | Josh Hazlewood |
| 6 | Sunil Narine | Varun Chakravarthy |
| 7 | Mohsin Khan | Nathan Ellis |
| 8 | Lockie Ferguson | Axar Patel |
| 9 | Nathan Ellis | Mohsin Khan |
| 10 | Axar Patel | Matheesha Pathirana |

## 5. Limits, stated plainly

- Prediction is modest: held-out correlation about 0.07 for batters and 0.22 for bowlers. Batting under pressure is much less predictable than bowling under pressure in this data.
- The batter interaction is a modest tuning-set result and is vulnerable to multiple-comparison optimism after about 30 variants. The bowler shrinkage change has a larger tuning-set gain. Legacy confirmation numbers are not independent evidence because they were used in earlier V3 gating.
- Ranks 6 to 10 of the batters overlap heavily with ranks 11 to 20 (see the rank intervals).
- The initial warm-up period is cross-fitted internally by match; every subsequent WP, leverage, pressure, resource-value and expected-value fold is trained only on earlier dates. Venue averages and ridge penalty CV are also past-only. The temporal validation table evaluates this chronologically cross-fit pipeline after warm-up, but it is diagnostic rather than a separately reserved final holdout.
- No pitch, weather, dew, fielding or ball-tracking data; bye and leg-bye run values are not recorded.
- Availability for the auction is unknown until retention lists are published.


## 6. Forward-in-time validation

See outputs/v3/temporal_validation.csv. Each row fits V3 on matches before a cutoff and evaluates the same players on the following six/seven months. This is a forward-only check of the rating fit on the existing credit tables. Upstream state and credit features are now generated by warm-up cross-fitting and forward-only chronological folds. No later match is used to construct a test-fold WP, leverage, pressure, resource-value, expected-value or venue feature. These windows remain diagnostic rather than a reserved final holdout because the broader V3 tuning process has already examined overlapping historical periods.

The final RR fit is regenerated from V3 ratings and V3 batter credit in outputs/v3/rr_fit/. The earlier phase-1 fit remains in outputs/tables/ for comparison.

## 7. Scope of the pressure objective

The ranked quantity is overall leverage-weighted NRAE, not the difference between a player's pressure performance and their own normal performance. The latter is shown separately as a raw descriptive contrast in the ratings files (raw_pressure_uplift); it is not context-adjusted and is not used to rank players. Consistency is likewise not part of the V3 score. Pressure-innings dispersion (press_innings_nrae_mad) is available as a descriptive stability diagnostic, but is sample-size sensitive.

## 8. Reproduction and caveats

The full pipeline now runs the acceptance suite automatically after all stages, including forward-only validation and the V3 RR fit. The 83 missing striker-to-playing-XI references and 40 duplicate playing-XI rows are exported to outputs/tables/playing_eleven_missing_strikers.csv and playing_eleven_duplicates.csv; they remain documented source anomalies rather than silently corrected records.


## 9. Reproduce

```bash
python run_all.py
```

Stages 31 (richer batter baseline), 30 (all experiment rounds, about 20 minutes), 32 (ratings) and 33 (this report).

## 10. Exact dropdown selections

**Batters**

1. Vaibhav Sooryavanshi (50284)
2. Abhishek Sharma (6281)
3. Namboori Tilak Varma (7897)
4. Phil Salt (5553)
5. Tim David (6396)
6. Ashutosh Sharma (8101)
7. Harry Brook (6280)
8. Suryakumar Yadav (1699)
9. Pathum Nissanka (6931)
10. Heinrich Klaasen (4260)

**Bowlers**

1. Jasprit Bumrah (2933)
2. Sunil Narine (781)
3. Rashid Khan (4722)
4. Bhuvneshwar Kumar (360)
5. Josh Hazlewood (830)
6. Varun Chakravarthy (6256)
7. Nathan Ellis (7920)
8. Axar Patel (2876)
9. Mohsin Khan (6669)
10. Matheesha Pathirana (8661)
