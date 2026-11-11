# Decision log

Every non-trivial choice, the reason, and the alternative rejected. Entries are in the order they were made.
Section A (setup and data), section B (pre-registered primary specification) were written and committed
before any player rating or ranking was computed. Later sections are appended as the work proceeds.

## A. Setup and data decisions (made before any ranking existed)

**D-01 Starting point.** The repository contained only the six CSVs and the problem statement PDF, so the
pipeline is built from scratch following `CLAUDE_CODE_HANDOVER.md`. The supplied
`context/rr_auction_context.md` was not in the repository. The RR layer therefore relies on the data plus
web search, and every outside fact is marked sourced or unverified. Raw CSVs had no hash prefix; they were
moved unchanged into `data/raw/`.

**D-02 Legal-ball rule (differs from the handover).** The handover says a legal ball is any row whose
`extras_type` is not "wide" and not "Overstep", and that "other" is legal. The data says the opposite.
With "other" legal, 244 overs have more than 6 legal balls and 150 innings exceed 120 legal balls. With
"other" treated as illegal, 1 over exceeds 6 and no innings exceeds 120. "other" rows also carry bat runs
(including sixes) and the same `extras_2_runs` pattern as "Overstep", so they are no-balls of another kind
(height or fielding no-balls). Adopted rule: illegal = wide, Overstep, other. Rejected: the handover rule,
because it breaks the 6-ball over. Consequence: sample-size counts differ slightly from the handover
(214 batters with 200+ balls faced versus 217 claimed, and so on, see `outputs/tables/data_quality.csv`).

**D-03 Balls faced.** A batter faces every delivery that is not a wide, including no-balls (standard
scoring). Bowler units are legal-ball "slots": one legal ball plus any wides and no-balls that preceded it,
so a bowler is charged for illegal deliveries without them counting as balls bowled.

**D-04 Reduced and unusable matches.** Excluded from win-probability training and from all pressure
analysis: matches with any of `first_inn_revised_overs`, `second_inn_revised_overs`, `revised_target` set,
plus matches whose result text mentions DLS or D/L although no revised field is set (4 such matches, a gap
in the flags). Also excluded: matches with no winner, matches whose first innings ends before 120 legal
balls without being all out and without a flag (5 matches, 12- or 16-over games that are not flagged), and
matches whose result string contradicts the ball data order. Counts are printed by `src/02_build_state.py`
and stored in `data_quality.csv`. 809 clean matches remain of 867 with ball data.

**D-05 Super overs.** Innings 3 and 4 (38 deliveries, 6 matches) are dropped. A tied match decided by a
super over keeps its 40 overs, the winner is `win_team_id`, and the chase target is the chasing total plus 1.

**D-06 Extras run values.** Per-type values are fitted on clean run-margin matches by least absolute
deviations with bounds [1, 6] (linear programme). Rejected: least squares, because a handful of matches
have margin errors of 8 to 10 runs from causes other than extras and they dominate a squared loss; LAD
also guarantees an in-sample error no worse than the 1-run rule, which is a feasible point. The penalty row
is fixed at 5 runs. `extras_2_runs` is added on top.

**D-07 Chase target is anchored to the result (differs from the handover).** The handover says to use the
reconstructed first-innings total plus 1 as the target. Evidence from stage 02, before any model existed:
the reconstruction error is about 2 runs per innings on average but with a long tail, and in 42% of
chases won by wickets the reconstructed chasing total is still below the reconstructed target when the
match ends. A target that is wrong by a few runs matters most exactly where pressure is highest, the last
overs of a close chase. The true target is public before the chase starts and can be recovered from the
result string: for "won by N runs" it is chasing total + N + 1; for "won by N wickets" it lies between the
score before the last ball + 1 and the final total, and the reconstructed value is clipped into that range;
for ties it is the chasing total + 1. This uses the result only to remove measurement error in a quantity
that was known during the match, so it is not outcome leakage. `config.json` keeps `target_mode` so the
reconstructed version can be run for comparison, and phase 2 reports the out-of-fold log loss of both.
Rejected: reconstructed target only.

**D-08 Wicket check.** Wickets lost in the chase equal 10 minus N in 418 of 419 "won by N wickets"
matches. The exception is match 20190 (IPL 2023, LSG v SRH), where the ball data shows 5 wickets and the
result string says "won by 6 wickets". The ball data is internally consistent, so this is treated as an
error in the result string (unverified against an outside scorecard).

**D-09 Opposition weights.** "T20I matches against associates weight 0.5" is applied per delivery by the
quality of the opposition: a batter's ball counts 0.5 when the bowling side is an associate, a bowler's
ball counts 0.5 when the batting side is an associate. An associate player facing a full member keeps
weight 1.0, because that is strong opposition. Full members: Afghanistan, Australia, Bangladesh, England,
India, Ireland, New Zealand, Pakistan, South Africa, Sri Lanka, West Indies, Zimbabwe. All A-team
tournament deliveries (comp 2670 and 3289) weigh 0.5. Rejected: down-weighting every ball of a match that
involves an associate, which would penalise associate players for meeting strong sides.

**D-10 Season.** Team-by-season effects use the calendar year of the match date, because the `season`
column mixes "2023" and "2023/24" labels.

## B. Pre-registered primary specification

Written before computing any player estimate. Anything changed later is logged in section D as post hoc.

1. **Match state** per delivery before the ball: legal balls bowled, balls left, score, wickets lost,
   current run rate; innings 2 adds target, runs needed, required rate and required minus current rate;
   runs and wickets in the previous 12 deliveries, dot-ball streak; leave-one-match-out venue average
   first-innings score shrunk to the tier mean with 3 pseudo-matches; competition tier.
2. **Win probability**: LightGBM classifier for "batting side wins" on the state features with an innings
   flag, 5-fold cross-validation grouped by match, out-of-fold predictions only. No team or player
   identity. Monotone constraints in the obvious directions (more runs needed and more wickets lost never
   help the chasing side) are used because leverage is a difference of predictions and an unconstrained
   tree ensemble makes those differences noisy. The unconstrained model is fitted as a comparison.
3. **Leverage**: expected absolute change in win probability over the next-ball outcomes dot, 1, 2, 3, 4,
   6, wicket, wide, no-ball, weighted by empirical frequency for the phase and innings, divided by the
   global mean. Hypothetical next states are scored by the model of the fold that did not see the match.
4. **Pressure score**: percentile of leverage among all deliveries of the same innings number (first
   innings deliveries ranked against first innings deliveries, chases against chases). Rejected readings:
   percentile inside each single innings, which would flag 20% of every blowout, and a global percentile,
   which puts almost all pressure in chases and leaves batting-first players with tiny samples. The global
   version is run as sensitivity variant F.
5. **Tiers**: Low below 50, Normal 50 to 80, High 80 to 95, Extreme 95 and above. Primary pressure sample:
   score at or above 80.
6. **Baselines**: out-of-fold LightGBM models without player identity for bat runs per ball faced,
   striker dismissal per ball faced, bowler runs per slot and bowler-credited wicket per slot. Wicket value
   in runs from a smoothed resource table fitted on first innings, R_w(b) = a_w (1 - exp(-b / t_w)).
7. **Credit**: batter NRAE = (bat runs - xRuns) - wicket value x (dismissed - xWkt) on balls faced, with
   dismissals charged to `dismissed_player_id` (run outs of the non-striker and dismissals off wides become
   dismissal-only records). Retired out carries no cost. Bowler NRAE = (xRuns - runs charged) + wicket
   value x (bowler wicket - xWkt) per slot, with wides and no-balls charged and byes and leg byes not.
   WPA = change in out-of-fold win probability, to the striker and with opposite sign to the bowler.
8. **Estimator**: weighted crossed ridge on ball-level NRAE with player normal effect, player pressure
   delta, opponent effect, own-team-by-season effect, venue, tier and an unpenalised pressure indicator.
   Penalties chosen by 5-fold cross-validation grouped by match over the grid in `config.json`.
   Cross-check: empirical Bayes shrinkage of raw pressure NRAE per 100 balls with match-clustered standard
   errors and method-of-moments prior variance.
9. **Weights**: recency half-life 24 months back from 2026-11-01; opposition weights as in D-09.
10. **Consistency**: per pressure innings or spell, hit = summed NRAE at or above 0; beta-binomial
    shrinkage; downside share as defined in the handover, also shrunk; consistency = hit rate minus
    downside share.
11. **Composite**: z-scores among eligible players, 0.40 Level + 0.25 Impact + 0.20 Consistency +
    0.15 Delta.
12. **Eligibility**: batters 60 pressure balls and 12 pressure innings; bowlers 48 pressure balls and 10
    pressure spells; both 150 total balls and an appearance in 2025 or 2026. Lowered only if fewer than 40
    qualify.
13. **Decision rule**: final order is the primary composite. A primary top-10 player whose top-10
    frequency across the sensitivity grid is below 0.40 is replaced by the best-ranked outsider at or above
    0.40. No manual overrides.
14. **Model-quality yardsticks for any later change**: out-of-fold log loss and calibration, split-half
    reliability of the ratings (mean Spearman correlation over 20 random match-half splits), season-split
    persistence, and bootstrap rank stability. Never the identity of the players in the list.

## C. Changes made while building phase 1 (after the pre-registration commit)

**D-11 Win-probability model changed before any player estimate existed.** Pre-registration item 2 named a
monotone LightGBM model. Out of fold it was clearly worse than a simple logistic model on a
resource-adjusted margin: log loss 0.5327 against 0.5220 overall and 0.4164 against 0.3975 in chases
(`outputs/tables/wp_model_metrics.csv`; an earlier, larger LightGBM setting scored 0.5567). Cause: every
ball of a match shares one label, so trees memorise matches through continuous features such as target
and venue average. The logistic model is also smooth, which matters because leverage is a difference of
predictions. Adopted: per-innings logistic regression on a degree-2 polynomial of (resource margin, balls
left, wickets lost, runs and wickets in the last 12 balls, dot streak), with the resource table fitted
inside each training fold. The version without momentum features has the same log loss (0.5221); momentum
is kept because the specification lists it in the match state. The decision was made on log loss and
calibration only, before stage 05 onwards had been written. The LightGBM models stay in the metrics table.

**D-12 Calibration tolerance.** With 809 matches, a 20-bin reliability table is dominated by match-level
noise. The acceptance check uses 10 bins and counts a bin as dense at 5,000 deliveries. The largest dense
gap is 0.026 and every bin is within two standard deviations of match-bootstrap noise
(`wp_calibration_bins.csv`).

**D-13 Resource curves must not cross.** The first fit of R_w(b) gave more expected runs with one wicket
down than with none late in an innings (few observations with 0 or 1 wickets down and 6 overs left), so
the wicket value was floored at zero there. A non-crossing penalty was added to the fit. Wicket values
for few wickets down at the death remain close to zero because the data say so: with 36 balls left the
observed remaining runs are 68.9, 69.2 and 68.4 for 0, 1 and 2 wickets down.

**D-14 Two bowler wickets in one slot.** A stumping off a wide followed by a wicket on the legal ball of
the same slot was being counted once (aggregation by max). Changed to a sum; found by an assertion that
credited wickets equal bowler-type dismissals.

**D-15 Level versus empirical Bayes agreement below 0.8.** Spearman 0.47 (batters) and 0.46 (bowlers) for
Level, 0.85 and 0.84 for the composite. Investigated as the specification requires: the ridge Level is
normal effect plus delta and uses all balls, the empirical Bayes Level uses pressure balls only. The
difference is structural. No change made.

**D-16 Ridge penalty at the edge of the grid.** For bowlers the delta penalty lands on the largest grid
value (30,000) and the cross-validated error is flat beyond 3,000 for both groups. The grid was not
extended in phase 1 because it was pre-registered; the meaning is that individual pressure deltas are not
identifiable. See section D for the consequence.

**D-17 Bootstrap design.** The eligible set and the ridge penalties are held fixed across resamples.
Re-deciding eligibility inside each resample would change the pool being ranked and make rank intervals
uninterpretable. The cost is intervals that are somewhat too narrow. Stated in FINDINGS.

**D-18 Sensitivity grid design.** One-at-a-time structural changes from the primary (14 configurations),
each crossed with 201 weight vectors (primary plus 200 Dirichlet draws, concentration 20). Grid top-10
frequency is the mean over configurations with equal weight per configuration, so the 200 weight draws
do not swamp the structural changes. A player who is not eligible in a configuration (for example an
uncapped player in "T20I only") scores zero there. Rejected: full cross product, which is dominated by
combinations nobody would run.

**D-19 Decision rule tie case.** If a primary top-10 player is below 0.40 and no outsider is at or above
0.40, he stays. The final list keeps primary order; a swapped-in outsider takes the position his primary
rank gives him among the ten.

**D-20 Persistence design.** Each half is rated from its own matches with thresholds at half scale and
without the recent-appearance rule (the early half has no 2025 or 2026 matches by construction).

**D-21 RR layer.** `context/rr_auction_context.md` was written from the data and a web search because it
was not supplied. "Would displace" requires the candidate's 80% rating interval to lie entirely above
the incumbent's interval. Overseas status is derived from the national side in the mapping file.
Availability is "unknown, check after retention list" for everyone.

## D. Phase 2a: audit of the phase 1 pipeline

**Clean clone.** `git clone` into an empty directory, `python run_all.py`, `pytest`: every stage ran,
24 tests passed (2 skipped because README and FINDINGS did not exist yet) and the seven main output
tables were byte-identical to the working copy (`cmp`). Runtime 7.4 minutes with another job running.

**Leakage hunt, item by item.**
- Matches scored by a model that saw them: none. Folds are assigned per match; the fold model applied to
  a match is the one trained without it, for realised and for hypothetical next-ball states. Tested.
- Resource table inside the win-probability model: fitted on training folds only.
- Expected runs and wickets: out of fold on the same match folds.
- Venue average: leave-one-match-out for the match itself, but it uses matches from other folds. This
  passes feature information, not labels, between folds. Left as is and listed as a limitation.
- Wicket-value table and next-ball outcome frequencies: fitted once on all clean matches. They are
  20-parameter and 54-number summaries with no player or result information. Left as is.
- Result-anchored target: uses the result string to recover a quantity that was public before the chase.
  Checked by test: chases won by wickets end at or above the target, chases lost by N end N+1 short.
- Wides counted as balls faced: zero (assertion and test). Run outs credited to bowlers: zero.
  Dismissals charged exactly once to `dismissed_player_id`: 10,379 of 10,379 costed wickets.
- Super overs and reduced matches downstream: zero rows.
- Duplicate ids, joins: every merge prints row counts and fails on any change; no player id has two
  names; no duplicate deliveries or slots (`outputs/tables/audit_integrity.csv`).

**Things the audit found.**
- `playing_eleven.csv` holds 40 duplicated (match, team, player) rows, 83 striker appearances with no
  playing-XI row, one delivery where striker equals non-striker and one bowler with 25 legal balls in an
  innings. None affects a result: appearances are counted as distinct matches.
- The audit sampler first drew an abandoned match and crashed; it now samples completed matches.
- A stage-08 figure failed when a point rating lay outside its bootstrap interval. Fixed by clipping the
  error bar; the cause (top-ranked players regress in resamples) is explained in FINDINGS.

**Scorecards by hand.** Ten seeded random matches (`outputs/tables/audit_scorecards.csv`): winner and
wickets agree with the result string in all ten; run-margin errors are +0.5 to +4.7 runs. One chase
(match 45499) reconstructs to 129 when the target was 138 or more and the side won: runs are missing from
the ball data for that innings. The anchored target absorbs this.

**Implausible rankings, cause sought in the code before touching any parameter.**
- Smallest pressure sample in a top 10: 85 balls (Vaibhav Sooryavanshi, 19 pressure innings). He passes
  the pre-registered thresholds. His rating comes from the Level component, which is the ridge normal
  effect plus delta, so it reflects 500-odd balls at a strike rate above 220, not 85 balls. No bug.
- Associate opposition: the largest share of pressure balls against associates or A-teams among the
  twenty listed players is 9%. No issue.
- High-volume finishers ranked near the bottom (`face_validity.csv`). Cause found in the baseline: it
  does not know how long the batter has been in. Residual bat runs per 100 balls are -26.8 on balls 1 to 3
  of an innings, -4.2 on balls 4 to 6 and +10 after ball 12. A finisher faces a far larger share of
  first balls than an opener, so the baseline is unfair to the role. This is tested as a model change in
  section E (role-aware baseline), not patched.
- Component scaling. After shrinkage the consistency component has a spread of 0.004 and the bowler delta
  0.05 per 100 balls, yet z-scoring gives each of them the same spread as Level. Shrinkage removed the
  noise and z-scoring put it back. Tested in section E.

## E. Phase 2b: model changes, judged on model-quality evidence only

**Adoption rule, written before any variant result was read.** Each variant is a full pipeline run in
`data/experiments/<tag>/`, scored by `src/eval_quality.py` (`outputs/tables/phase2_experiments.csv`).
- A change to the win-probability model, the target, the leverage definition or the baseline is adopted
  only if its own out-of-fold metric improves (log loss, leverage versus realised swing, baseline RMSE
  and log loss) and the split-half reliability of the rating does not fall by more than two standard
  errors in either group.
- A change to how ratings are built (opposition term, component scaling) is adopted only if split-half
  reliability of the rating rises by more than two standard errors in at least one group, does not fall
  by more than two standard errors in the other, and bootstrap stability (top-10 probability of the
  top 10, 80% rank-interval width of the top 20) is not worse.
- Split-half reliability is the mean Spearman correlation over 20 random match-half splits; its standard
  error is the SD across splits divided by the square root of 20.
- Who is in the top 10 is not looked at when deciding. The lists are compared only after the decision.
- Any adopted change is a post-hoc change to the pre-registered specification, and the phase 1 results
  stay in `outputs/phase1/`.
