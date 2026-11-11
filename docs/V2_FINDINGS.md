# V2: a fresh build of the pressure rating

This is an independent second design, made from the six supplied CSVs and the problem statement only. The ball-level preparation (legal balls, extras, match state, out-of-fold win probability, expected runs and wickets) is reused from `docs/FINDINGS.md` because it is data engineering that was checked against scorecards and published figures. Everything about how players are rated was redesigned around one question: **which method best predicts a player's future performance when the match is on the line?** Every table is in `outputs/v2/`, produced by `src/20_v2_search.py`, `21_v2_rate.py` and `22_v2_report.py`.

## 1. Result

Rating is runs per 100 balls above an average player in the same situation (same phase, wickets, required rate, bowler type, venue), measured with every ball weighted by how much it can move the match, adjusted for the opponents faced and shrunk toward the average for small samples. The interval is the 80% interval over 1,000 resamples of matches.

### Top 10 batters (`top10_batters.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) | Pressure balls |
|---|---|---|---|---|---|---|
| 1 | Vaibhav Sooryavanshi (50284) | 15.25 | 8.5 to 22.2 | 1 to 8 | 0.93 | 85 |
| 2 | Abhishek Sharma (6281) | 12.76 | 6.1 to 19.4 | 1 to 18 | 0.84 | 300 |
| 3 | Phil Salt (5553) | 10.35 | 5.6 to 14.1 | 2 to 20 | 0.76 | 200 |
| 4 | Namboori Tilak Varma (7897) | 10.03 | 4.7 to 15.3 | 2 to 27 | 0.69 | 514 |
| 5 | Tim David (6396) | 9.67 | 4.6 to 14.4 | 2 to 27 | 0.69 | 321 |
| 6 | Suryakumar Yadav (1699) | 7.99 | 4.1 to 11.8 | 3 to 31 | 0.53 | 478 |
| 7 | Heinrich Klaasen (4260) | 7.47 | 4.1 to 10.5 | 4 to 33 | 0.46 | 256 |
| 8 | Ashutosh Sharma (8101) | 7.39 | 1.8 to 13.0 | 3 to 59 | 0.45 | 112 |
| 9 | Pathum Nissanka (6931) | 6.73 | 2.3 to 10.8 | 4 to 54 | 0.38 | 263 |
| 10 | Harry Brook (6280) | 6.54 | 2.4 to 10.7 | 5 to 51 | 0.35 | 140 |

1. **Vaibhav Sooryavanshi**: strike rate 238 under pressure against 220 otherwise, 202 runs and 4 dismissals in 85 pressure balls; 9% of them against associate or A-team sides.
2. **Abhishek Sharma**: strike rate 202 under pressure against 185 otherwise, 606 runs and 18 dismissals in 300 pressure balls; 4% of them against associate or A-team sides.
3. **Phil Salt**: strike rate 170 under pressure against 171 otherwise, 340 runs and 7 dismissals in 200 pressure balls; 0% of them against associate or A-team sides.
4. **Namboori Tilak Varma**: strike rate 167 under pressure against 137 otherwise, 856 runs and 20 dismissals in 514 pressure balls; 2% of them against associate or A-team sides.
5. **Tim David**: strike rate 192 under pressure against 172 otherwise, 615 runs and 23 dismissals in 321 pressure balls; 0% of them against associate or A-team sides.
6. **Suryakumar Yadav**: strike rate 168 under pressure against 167 otherwise, 804 runs and 24 dismissals in 478 pressure balls; 1% of them against associate or A-team sides.
7. **Heinrich Klaasen**: strike rate 184 under pressure against 163 otherwise, 470 runs and 14 dismissals in 256 pressure balls; 0% of them against associate or A-team sides.
8. **Ashutosh Sharma**: strike rate 181 under pressure against 160 otherwise, 203 runs and 7 dismissals in 112 pressure balls; 6% of them against associate or A-team sides.
9. **Pathum Nissanka**: strike rate 153 under pressure against 133 otherwise, 403 runs and 13 dismissals in 263 pressure balls; 5% of them against associate or A-team sides.
10. **Harry Brook**: strike rate 159 under pressure against 166 otherwise, 223 runs and 10 dismissals in 140 pressure balls; 0% of them against associate or A-team sides.

Figure: `v2_top10_batters.png`.

### Top 10 bowlers (`top10_bowlers.csv`)

| Rank | Player (id) | Rating | 80% interval | 80% rank interval | P(top 10) | Pressure balls |
|---|---|---|---|---|---|---|
| 1 | Jasprit Bumrah (2933) | 10.92 | 6.4 to 15.3 | 1 to 12 | 0.88 | 366 |
| 2 | Varun Chakravarthy (6256) | 9.90 | 5.4 to 14.5 | 1 to 17 | 0.82 | 401 |
| 3 | Bhuvneshwar Kumar (360) | 9.63 | 4.8 to 14.4 | 1 to 23 | 0.76 | 560 |
| 4 | Josh Hazlewood (830) | 9.63 | 5.4 to 13.8 | 1 to 17 | 0.80 | 333 |
| 5 | Rashid Khan (4722) | 9.43 | 5.8 to 13.0 | 2 to 14 | 0.84 | 484 |
| 6 | Sunil Narine (781) | 8.28 | 4.8 to 11.5 | 2 to 20 | 0.69 | 351 |
| 7 | Mohsin Khan (6669) | 6.66 | 2.2 to 11.0 | 3 to 54 | 0.47 | 151 |
| 8 | Lockie Ferguson (4692) | 6.34 | 2.3 to 10.5 | 3 to 51 | 0.42 | 248 |
| 9 | Nathan Ellis (7920) | 6.14 | 2.9 to 9.4 | 5 to 41 | 0.38 | 247 |
| 10 | Axar Patel (2876) | 6.01 | 2.2 to 9.7 | 4 to 52 | 0.36 | 446 |

1. **Jasprit Bumrah**: economy 7.07 under pressure against 7.15 otherwise, 20 wickets in 366 pressure balls; 2% against associate or A-team sides.
2. **Varun Chakravarthy**: economy 7.59 under pressure against 8.16 otherwise, 25 wickets in 401 pressure balls; 0% against associate or A-team sides.
3. **Bhuvneshwar Kumar**: economy 8.87 under pressure against 8.04 otherwise, 39 wickets in 560 pressure balls; 0% against associate or A-team sides.
4. **Josh Hazlewood**: economy 8.17 under pressure against 8.29 otherwise, 24 wickets in 333 pressure balls; 0% against associate or A-team sides.
5. **Rashid Khan**: economy 7.40 under pressure against 7.40 otherwise, 41 wickets in 484 pressure balls; 1% against associate or A-team sides.
6. **Sunil Narine**: economy 6.74 under pressure against 6.80 otherwise, 14 wickets in 351 pressure balls; 0% against associate or A-team sides.
7. **Mohsin Khan**: economy 8.41 under pressure against 8.51 otherwise, 11 wickets in 151 pressure balls; 0% against associate or A-team sides.
8. **Lockie Ferguson**: economy 10.03 under pressure against 8.53 otherwise, 14 wickets in 248 pressure balls; 2% against associate or A-team sides.
9. **Nathan Ellis**: economy 8.49 under pressure against 8.06 otherwise, 16 wickets in 247 pressure balls; 0% against associate or A-team sides.
10. **Axar Patel**: economy 7.38 under pressure against 7.97 otherwise, 24 wickets in 446 pressure balls; 1% against associate or A-team sides.

Figure: `v2_top10_bowlers.png`.

## 2. The method in six steps

1. **Clean the ball data.** Legal deliveries (wides and every no-ball type excluded), runs reconstructed for extras, super overs and rain-reduced matches removed, the chase target recovered exactly.
2. **Win probability for every ball.** A logistic model on the resource-adjusted margin, scored out of fold so no match is rated by a model that saw it.
3. **Pressure is leverage.** For each ball, the expected absolute swing in win probability over everything the next ball could be. A tight finish has high leverage; a dead game has almost none.
4. **Credit above expectation.** Expected runs and wicket probability from a model that knows the situation and the batter's stage of innings but not who the players are. Net runs above expected combines runs and the run value of a wicket.
5. **Rate players with a hierarchical ridge.** One regression gives each batter and bowler an effect, adjusting for the opponents faced, team strength by year, venue and competition. Each ball is weighted by its leverage and by how recent it is, so a player's rating is dominated by the balls that mattered.
6. **Choose every design option by prediction, not by taste.** See the next section.

## 3. How the design was chosen

Each trial fits the rating on part of the data and measures how well it predicts the same players' pressure performance in data it never saw, using weighted rank correlation. Tuning used 5 rolling forward-in-time windows plus 20 random half splits (25 trials). A separate set of 22 trials (2 later time windows plus 20 other random splits) was never used to choose anything.

**Adoption rule.** An option moves away from the reference setup only if it is better by more than two standard errors of the paired difference across the tuning trials. A first attempt without this rule (3 folds, free coordinate search) overfit: it scored 0.03 and -0.02 on later data against 0.24 and 0.08 for the plain setup. That failure is why the rule exists. The reference setup is leverage power 1, 24-month half-life, ridge penalty 3,000, associates at half weight, opponent adjustment on.

Chosen configuration (`chosen_config.json`):

| group | half_life | alpha | assoc_w | lam | role_prior | opp_adjust |
|---|---|---|---|---|---|---|
| batters | 24.0 | 1.00 | 0.50 | 3000.00 | False | True |
| bowlers | none | 1.00 | 1.00 | 3000.00 | False | True |

Every option tried, as a difference from the reference (`search_log.csv`; positive = better; adopted only when z > 2):

| role | option | value | reference | diff_vs_reference | se | z | adopted |
|---|---|---|---|---|---|---|---|
| batters | lam | 300.0 | 3000.0 | 0.004 | 0.007 | 0.625 | False |
| batters | lam | 1000.0 | 3000.0 | 0.003 | 0.003 | 1.028 | False |
| batters | lam | 10000.0 | 3000.0 | -0.002 | 0.002 | -1.122 | False |
| batters | lam | 30000.0 | 3000.0 | -0.006 | 0.003 | -1.829 | False |
| batters | alpha | 0.0 | 1.0 | -0.021 | 0.013 | -1.647 | False |
| batters | alpha | 0.5 | 1.0 | -0.008 | 0.006 | -1.430 | False |
| batters | alpha | 1.5 | 1.0 | -0.000 | 0.006 | -0.063 | False |
| batters | alpha | 2.0 | 1.0 | -0.013 | 0.010 | -1.287 | False |
| batters | half_life | 6.0 | 24.0 | -0.010 | 0.011 | -0.963 | False |
| batters | half_life | 12.0 | 24.0 | -0.002 | 0.005 | -0.436 | False |
| batters | half_life | 48.0 | 24.0 | -0.004 | 0.003 | -1.220 | False |
| batters | half_life |  | 24.0 | -0.013 | 0.006 | -2.110 | False |
| batters | assoc_w | 0.25 | 0.5 | -0.000 | 0.001 | -0.536 | False |
| batters | assoc_w | 1.0 | 0.5 | 0.002 | 0.001 | 1.252 | False |
| batters | role_prior | True | False | -0.015 | 0.010 | -1.505 | False |
| batters | opp_adjust | False | True | 0.001 | 0.001 | 1.523 | False |
| batters | score | wpa | nrae | -0.045 | 0.017 | -2.563 | False |
| batters | score | blend0.25 | nrae | -0.009 | 0.004 | -2.167 | False |
| batters | score | blend0.5 | nrae | -0.010 | 0.006 | -1.753 | False |
| batters | score | blend1 | nrae | -0.017 | 0.009 | -1.903 | False |
| bowlers | lam | 300.0 | 3000.0 | 0.001 | 0.005 | 0.144 | False |
| bowlers | lam | 1000.0 | 3000.0 | 0.001 | 0.002 | 0.271 | False |
| bowlers | lam | 10000.0 | 3000.0 | -0.003 | 0.002 | -2.252 | False |
| bowlers | lam | 30000.0 | 3000.0 | -0.004 | 0.002 | -1.790 | False |
| bowlers | alpha | 0.0 | 1.0 | -0.025 | 0.008 | -3.018 | False |
| bowlers | alpha | 0.5 | 1.0 | -0.000 | 0.004 | -0.004 | False |
| bowlers | alpha | 1.5 | 1.0 | -0.006 | 0.006 | -1.057 | False |
| bowlers | alpha | 2.0 | 1.0 | -0.010 | 0.011 | -0.894 | False |
| bowlers | half_life | 6.0 | 24.0 | -0.043 | 0.009 | -4.671 | False |
| bowlers | half_life | 12.0 | 24.0 | -0.021 | 0.005 | -4.628 | False |
| bowlers | half_life | 48.0 | 24.0 | 0.012 | 0.003 | 3.814 | True |
| bowlers | half_life |  | 24.0 | 0.024 | 0.007 | 3.550 | True |
| bowlers | assoc_w | 0.25 | 0.5 | -0.002 | 0.001 | -2.538 | False |
| bowlers | assoc_w | 1.0 | 0.5 | 0.004 | 0.001 | 3.583 | True |
| bowlers | role_prior | True | False | -0.024 | 0.007 | -3.635 | False |
| bowlers | opp_adjust | False | True | -0.000 | 0.001 | -0.194 | False |
| bowlers | score | wpa | nrae | -0.029 | 0.016 | -1.856 | False |
| bowlers | score | blend0.25 | nrae | 0.005 | 0.003 | 1.607 | False |
| bowlers | score | blend0.5 | nrae | 0.003 | 0.005 | 0.672 | False |
| bowlers | score | blend1 | nrae | 0.002 | 0.007 | 0.301 | False |

In words. For batters nothing beat the reference. For bowlers, dropping the recency decay and counting all opposition at full weight both passed the rule. That fits bowling quality being steadier over years than batting form, though the data only show the prediction gain, not the reason.

## 4. Does it predict anything? (confirmation trials, never used for tuning)

| role | method | objective | se | corr_nrae_target | corr_wpa_target | players |
|---|---|---|---|---|---|---|
| batters | V2 (chosen) | 0.065 | 0.013 | 0.094 | 0.037 | 121 |
| batters | Reference setup | 0.065 | 0.013 | 0.094 | 0.037 | 121 |
| batters | No leverage weighting | 0.038 | 0.014 | 0.064 | 0.011 | 121 |
| batters | Almost no shrinkage | 0.035 | 0.014 | 0.065 | 0.006 | 121 |
| batters | Raw pressure strike rate | 0.028 | 0.012 | 0.087 | -0.031 | 121 |
| batters | Raw pressure NRAE | 0.009 | 0.013 | 0.035 | -0.017 | 121 |
| bowlers | V2 (chosen) | 0.189 | 0.017 | 0.203 | 0.174 | 116 |
| bowlers | Almost no shrinkage | 0.156 | 0.013 | 0.160 | 0.151 | 116 |
| bowlers | Reference setup | 0.153 | 0.015 | 0.164 | 0.141 | 116 |
| bowlers | No leverage weighting | 0.146 | 0.016 | 0.155 | 0.137 | 116 |
| bowlers | Raw pressure NRAE | 0.120 | 0.016 | 0.130 | 0.111 | 116 |
| bowlers | Raw pressure economy | 0.088 | 0.015 | 0.125 | 0.050 | 116 |

Figure: `v2_confirmation.png`. Reading it:

- The rating beats the obvious scouting statistics. Raw pressure strike rate scores 0.028 for batters and raw pressure economy 0.088 for bowlers, against 0.065 and 0.189.
- For batters, leverage weighting adds 0.028 and shrinkage adds 0.030 (each about 2.2 to 2.4 standard errors of a single mean, a loose guide).
- For bowlers, the same two ingredients add 0.006 and -0.003 on the confirmation trials, which is within noise. Leverage weighting did win clearly on the tuning trials (section 3, z = 3.0), so it stays, but this is weaker evidence for bowlers than for batters.
- What did help bowlers on the confirmation trials is the pair of choices made in tuning (no recency decay, full weight for all opposition): 0.189 against 0.153 for the reference setup.
- The size of the effect is modest and should not be oversold: a correlation of about 0.07 for batters and 0.19 for bowlers. Pressure performance is only partly predictable from past pressure performance. Batters are much harder to predict than bowlers.

## 5. How the lists compare with earlier builds

- Batters: 10 of 10 players are the same as the phase 3 list in `docs/FINDINGS.md`; 7 of 10 are the same as the first build.
- Bowlers: 9 of 10 players are the same as the phase 3 list in `docs/FINDINGS.md`; 9 of 10 are the same as the first build.
  - New in V2 against phase 3: Lockie Ferguson; dropped: Wanindu Hasaranga. The difference comes from the bowler recency decision above: without a decay, bowlers whose best form is older are no longer discounted.

Two designs reached the same batter set. That is the strongest robustness evidence in this repository, stronger than any single interval.

## 6. Limits

- Held-out correlations are small. A rank is a best estimate; the intervals in section 1 are wide for ranks 6 to 10.
- Baselines, win probability and pressure flags were fitted on all matches (identity-free models). Strictly, that lets a little future league-wide information into past ratings. It cannot favour any player.
- The tuning and confirmation windows overlap in the data they train on; only the test windows are disjoint.
- No pitch, weather, dew or fielding data. Run values of byes and leg byes are unrecorded.
- The bootstrap holds eligibility and penalties fixed, so intervals are somewhat narrow.
- Sooryavanshi tops the batters on 85 pressure balls; his rating leans on his many other leveraged balls and the interval is wide (see section 1).

## 7. Reproduce

```bash
python run_all.py 20
```

Stages 20 to 22 need the credit tables from stages 01 to 06 (`python run_all.py` builds everything).

## Exact dropdown selections

**Batters**

1. Vaibhav Sooryavanshi (50284)
2. Abhishek Sharma (6281)
3. Phil Salt (5553)
4. Namboori Tilak Varma (7897)
5. Tim David (6396)
6. Suryakumar Yadav (1699)
7. Heinrich Klaasen (4260)
8. Ashutosh Sharma (8101)
9. Pathum Nissanka (6931)
10. Harry Brook (6280)

**Bowlers**

1. Jasprit Bumrah (2933)
2. Varun Chakravarthy (6256)
3. Bhuvneshwar Kumar (360)
4. Josh Hazlewood (830)
5. Rashid Khan (4722)
6. Sunil Narine (781)
7. Mohsin Khan (6669)
8. Lockie Ferguson (4692)
9. Nathan Ellis (7920)
10. Axar Patel (2876)
