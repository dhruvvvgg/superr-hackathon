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

**D-07 Chase target uses only first-innings reconstruction.** The target supplied to chase-state features
is the rounded reconstructed first-innings total plus one. It is not recovered or clipped from the final
score, run margin, wickets remaining, winner, or result string. This can introduce measurement error because
extras are incompletely represented in the source data, but it preserves the chronology of the feature:
the target is fixed before the second innings begins. Result-anchored target reconstruction is rejected
because it imports final-match information into an input used to predict the match outcome.

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

**D-12 Calibration tolerance (revised after chronological cross-fitting).** Calibration is reported
with 10 equal-width bins per innings and match-clustered bootstrap uncertainty. The acceptance gate
does not require every dense bin to be within an arbitrary 3 percentage points: it requires a maximum
dense-bin gap no larger than 8 percentage points and no more than one bin outside its 2-SD
match-bootstrap band. The exact gap and uncertainty are reported in `wp_calibration_bins.csv`;
this is a diagnostic tolerance, not a claim of perfect calibration. Log loss against the state-free
baseline remains a separate predictive acceptance check.

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

**Results** (`outputs/tables/phase2_experiments.csv`; "before" is the phase 1 specification, tag `base`).

| Attempt | Reason for trying | Own metric, before to after | Split-half rating, batters / bowlers (before 0.080 / 0.113, SE about 0.016) | Decision |
|---|---|---|---|---|
| Reconstructed target (`target_recon`) | the handover's target definition | WP log loss 0.5220 to 0.5236 (worse) | 0.067 / 0.117 | rejected, anchored target stays |
| Monotone LightGBM win probability (`wp_gbm`) | originally pre-registered model | WP log loss 0.5220 to 0.5327 (worse) | 0.172 / 0.106 | rejected |
| Win probability without momentum (`wp_nomom`) | simpler model | log loss 0.5220 to 0.5221, calibration gap 0.026 to 0.036, leverage validity 0.57 to 0.46 | 0.126 / 0.224 | rejected |
| RMS leverage (`lev_rms`) | weights large swings more | leverage versus realised swing, Spearman 0.57 to 0.51 (worse) | 0.025 / 0.155 | rejected |
| Role-aware baseline (`role_aware`) | audit finding: new batters score 27 per 100 below baseline | batter xRuns RMSE 1.7200 to 1.7107, bowler 1.7554 to 1.7459; xWkt log loss 0.2079 to 0.2075 and 0.2050 to 0.2046; ridge CV error 7.599 to 7.577 and 7.612 to 7.590 | 0.060 / 0.119 (both within 2 SE) | **adopted** |
| Opposition-team-by-season term (`opp_ts`) | explicit opposition-strength rating | ridge CV error 7.5987 to 7.5979 and 7.6115 to 7.6119 | 0.076 / 0.116 | rejected, no gain |
| Prior-SD scaling of components (`prior_sd`) | audit finding: z-scoring re-inflates shrunk noise | not applicable | 0.053 / 0.155; batter rank-interval width 44.9 to 50.2 (worse) | rejected, fails the stability condition |
| Role-aware plus prior-SD (`role_prior`) | combination | as role-aware | 0.035 / 0.145 against 0.060 / 0.119 for role-aware alone | rejected |
| Role-aware, prior-SD and opposition term (`role_prior_opp`) | combination | as role-aware | 0.028 / 0.149 | rejected |

Not run as separate variants, with the reason:
- Better handling of extras: the fitted values against the 1-run rule are already compared in
  `extras_calibration.csv` (margin MAE 2.14 against 2.17, out of sample 2.17). The real gain came from
  anchoring the target, tested above.
- Bowler matchup adjustment: batter hand, pace or spin and bowling type are already features of both
  baselines, so the baseline is matchup-aware; the ridge then adjusts for the individual opponent.

**Post-hoc change P-1: role-aware baseline.** `config.json` `baseline.role_aware` is now true. The
expected-runs and expected-wicket models for batters and bowlers additionally see the number of balls the
striker has already faced in the innings and his batting position. Evidence as in the table. This changes
pre-registration item 6. It was adopted under the rule written before the results were read. The phase 1
lists are in `outputs/phase1/` and are shown next to the final lists in FINDINGS, "What changed in
phase 2".

**What the experiments say about the yardstick itself.** Split-half reliability moved by up to 0.11
between variants that only change which balls are flagged as pressure, far more than its split-to-split
standard error. It is a noisy yardstick at this sample size. That is why the rule put each change's own
out-of-fold metric first and used reliability as a guard, and why two variants with higher reliability
in one group (`wp_gbm`, `wp_nomom`) were still rejected.

**The component-scaling idea was mine and it failed its test.** It is logged as rejected, with the
numbers, and the pre-registered z-scoring stays.

## F. Phase 2c: final run

- `config.json` now has `baseline.role_aware: true`; nothing else changed from the pre-registered
  specification except the items logged above (D-02, D-07, D-11, P-1).
- Full run from scratch, then a second run from a fresh `git clone`: all 28 output tables and
  `docs/FINDINGS.md` byte-identical between the two, 26 tests pass in both. Runtime 5.4 minutes.
- `docs/FINDINGS.md` is written by `src/11_report.py` from the tables, so its numbers cannot drift from
  the outputs. The only hand-typed numbers are the experiment notes in `docs/phase2_verdicts.json` and
  this file; they were checked against `outputs/tables/phase2_experiments.csv`.
- Decision rule in the final run: no batter below the 0.40 grid threshold. Among bowlers Jason Holder
  (rank 10, grid frequency 0.31) is below it, and no outsider reaches 0.40, so the primary list stands.
- Final lists differ from phase 1 by one name in each group (Fakhar Zaman for Prabhsimran Singh,
  Jason Holder for Taskin Ahmed, ranks 10 and 11 swapping) and by order within the top 10. Cause: P-1.

## G. Closing pass: supplied context file

**D-22 Context file.** The supplied `context/rr_auction_context.md` replaced the one assembled in phase 1
(D-01, D-21). Differences that mattered: the retention deadline is 17 November, not 15 November; IPL 2027
is a mini-auction on 16 December 2026 with a mega auction ahead of 2028; squad limits are 25 maximum and 18
minimum; overseas limits remain unconfirmed. Section 9 of FINDINGS and the squad-rule paragraph were
rewritten from it. No rating, ranking or shortlist logic changed, because the layer never used the old
rule text. One discrepancy is left open: the file's secondary source says RR won eight league matches in
2026 and the match data shows nine wins in 16 completed matches.

**D-23 Open items closed or left open.**
- Closed: availability stays "unknown, check after retention list" (lists due 17 November, not public).
- Closed: the two README and DECISIONS statements that the context file was missing are corrected.
- Left open, needs data not available here: retention and release outcomes, RR purse and slots, overseas
  limits, the 8 versus 9 wins discrepancy. Re-run `python run_all.py 09` after the lists are public.

## H. Final pass: online cross-check and source overrides

Rule adopted for this pass: where an outside source and the supplied data disagree, the outside source
overrides only if it is specific, checkable and consistent with the ball data. Each override is a named
entry in `config.json` `source_overrides`, applied in stage 02, asserted against the raw string, tested,
and listed here. The raw CSVs are never edited. Where a source is weak or only restates a rule, the item
stays "assumed" in the context file and nothing in the pipeline changes.

**D-24 Match 20190 result (override).** Supplied result "Lucknow Super Giants Won by 6 wickets". Scorecards
(ESPNcricinfo and four others) show LSG won by 5 wickets, SRH 121/8, LSG 127/5 in 16 overs. The ball data
agrees (5 wickets lost, 96 legal balls), which confirms the D-08 suspicion. Override sets the wickets in
the result to 5. The wicket check is now 419 of 419. No rating, target or model input changes, because for
a chase won by wickets the result string feeds only that check.

**D-25 Confirmed, no change.** Sooryavanshi's IPL 2026 batting rebuilt from the ball data is 776 runs, average
48.5, strike rate 237.3, identical to the published figures. RR's 2026 playoffs in the data (Eliminator won
by 47 runs against SRH, Qualifier 2 lost to GT by 7 wickets) match the reports. These checks validate the
parser, the legal-ball rule and the dismissal handling on real records.

**D-26 Closed.** RR's "eight wins" is the league record (8 league wins plus the Eliminator win). The
earlier note of a discrepancy (D-22) is withdrawn.

**D-27 Squad rules.** At most 25 players, at least 18, at most 8 overseas confirmed for the 2026 cycle by
several outlets. Assumed unchanged for 2027. The 4-overseas playing XI limit has only one weak source.
Overseas fee cap (lower of INR 18 crore and the mega-auction maximum) noted, unverified for 2027.
FINDINGS section 9 updated.

**D-28 Not changeable from outside sources.** Retention and release lists (due 17 November, not public),
RR's 2027 purse and slots, and availability of every player.

**D-29 Phase 2 experiments not re-run.** The override changes one string that only the wicket check reads,
so no experiment metric can move. The scorecard in `phase2_experiments.csv` stands. Every other table was
regenerated from scratch.

## I. Phase 3: best rating the supplied data can support

Goal given: improve the model in any way possible using only the supplied datasets. Rule: judge on
held-out predictive validity, not on who appears in the lists.

**D-30 New yardstick.** Rating-versus-rating split-half correlation (phase 2) can reward stable noise.
Replaced for selection by held-out prediction: rate from half A of the matches, correlate with the same
players' raw pressure NRAE and WPA per 100 balls in half B (weighted Spearman, weights = held-out pressure
balls), 20 random splits in both directions, paired across candidates. A 2022-24 to 2025-26 test was
reserved for confirmation. Selection rule written before adopting: highest sum of the four random-split
correlations, and it must beat the old composite on the temporal NRAE check. Stages 12 and 13.

**D-31 Findings (outputs/tables/phase3_candidates.csv).** Used alone and predicting held-out pressure NRAE:
Level 0.051 (batters) and 0.129 (bowlers); delta 0.035 and 0.090; consistency -0.005 and 0.087; impact
-0.037 and 0.084; old composite 0.035 and 0.115. The three components that held 60% of the specified
weight predicted nothing beyond Level, and impact was negative for batters.

**D-32 Candidate: leverage-weighted level.** The ridge is refitted with every ball weighted by its leverage
(power 1, weights clipped to 0.05 to 10 and normalised to mean 1). It is a continuous version of the pressure
definition (no cutoff, no discarded balls) and it uses far more data than the 20% pressure sample. Paired
against the old composite, held-out NRAE: batters +0.025 (SE 0.008), bowlers +0.024 (SE 0.007); held-out
WPA: batters +0.019 (SE 0.007), bowlers -0.003 (SE 0.006). Temporal confirmation beats the old composite on
NRAE in both groups (0.128 against 0.111 and 0.308 against 0.255). Leverage power 2 and power 0.5 are worse
or equal. Recomputed after retuning the ridge penalties (3,000 and 30,000 for both groups): same picture.

**D-33 Adopted as post-hoc change P-2.** `config.json`: `ridge.lev_alpha` 1.0 and `composite_weights`
level 1, others 0. The specified weights live on as `composite_weights_spec`, used by the old-composite
comparison and by the sensitivity configuration "spec weights". `sensitivity_weights` (0.7, 0.1, 0.1, 0.1)
centre the Dirichlet draws so the weight grid still tests the other components. Phase 1 and phase 2
results are kept in `outputs/phase1/` and `outputs/phase2/`.

**D-34 Caveats recorded, not hidden.**
- On the temporal test the plain unweighted level scores higher than the leverage-weighted level for
  batters (NRAE 0.174 against 0.128, WPA 0.079 against 0.010) and the old composite is higher on WPA for
  bowlers. One draw of about 100 players has no usable standard error. The random-split evidence, which
  has 40 trials per candidate, favours leverage weighting. The choice is a judgement between the two.
- The selection used the same random splits that were explored, so some optimism is expected. The
  temporal split was never used for choosing.
- Absolute predictive correlations stay small (batters about 0.06, bowlers about 0.14). Split-half
  reliability of the rating rose from 0.06 to 0.10 (batters) and 0.12 to 0.16 (bowlers).
- The brief asks for consistency and for a comparison with a player's usual level. Both are still computed,
  shown and tested as sensitivity configurations; the data simply do not support giving them weight.
- Checked for role bias: correlation of the rating with death-over share, chase share and weak-opposition
  share is between -0.06 and 0.10 for both groups.

**D-35 Tried and rejected.** Averaging the five win-probability models: log loss 0.5217 against 0.5220,
no gain, win probability unchanged. Rating variants that mix level with impact (0.8/0.2, 0.7/0.3) gain on
batter WPA but lose on NRAE; none beat plain leverage-weighted level on the sum of the four correlations.

**D-36 Decision rule outcome.** No batter below 0.40 grid frequency. Bowler Wanindu Hasaranga (rank 10,
grid 0.398) is below it; no outsider reaches 0.40, so the primary list stands.

## J. V2: independent rebuild of the rating, chosen by forward-in-time prediction

Instruction: set the earlier specification aside, think only from the six CSVs and the problem statement,
and build the best model possible. Reused as is: the verified ball-level preparation (stages 01 to 06).
Redesigned: the rating model, its tuning and its validation. Outputs in `outputs/v2/`, report in
`docs/V2_FINDINGS.md`. The older results stay in `outputs/tables/`, `outputs/phase1/`, `outputs/phase2/`.

**D-37 Question and yardstick.** The rating should predict a player's future pressure performance. Trials fit
on part of the data and score against the same players' later pressure NRAE and WPA per 100 balls (weighted
Spearman). Tuning trials: five rolling six-month windows plus 20 random half splits. Confirmation trials
(never used to choose): two later windows plus 20 random half splits with a different seed.

**D-38 First attempt overfit, and was rejected.** A free coordinate search on three overlapping 12-month
folds (about 70 players each) pushed the batter ridge penalty to the edge of its grid, chose a WPA score
variant, and scored 0.03 and -0.02 on the confirmation folds against 0.24 and 0.08 for the plain setup. Cause:
about 70 players per fold gives a standard error near 0.12 per fold, so the search was fitting noise. It is
kept in the log because it is the reason for the rule below.

**D-39 Adoption rule.** Start from a stated reference (leverage power 1, 24-month half-life, ridge penalty
3,000, associates at 0.5, no role prior, opponent adjustment on). Move an option only if the paired
difference in the objective is above two standard errors across 25 tuning trials. Result: nothing moves for
batters; for bowlers recency decay is removed (z 3.6) and associates go to full weight (z 3.6). Role prior,
WPA or blended scores, other leverage powers and other penalties never pass.

**D-40 Confirmation (outputs/v2/confirm.csv).** Held-out correlation, mean over 22 trials: batters 0.065
against 0.028 for raw pressure strike rate and 0.009 for raw pressure NRAE; bowlers 0.189 against 0.088 for
raw pressure economy and 0.120 for raw pressure NRAE; the reference setup scores 0.153 for bowlers. For
batters leverage weighting and shrinkage each add about 0.03; for bowlers they are within noise on the
confirmation trials and rest on the tuning evidence (z 3.0 for leverage weighting).

**D-41 Eligibility.** At least 40 pressure balls (the bar used in validation), 150 balls in total and an
appearance in 2025 or 2026. This widens the pool to 180 batters and 189 bowlers. The shrinkage handles small
samples, so a higher bar is not needed for fairness.

**D-42 Rating scale.** The rating is the ridge player effect (plus nothing else) in NRAE per 100 balls, i.e.
runs per 100 balls above an average player in the same situation. No z-scoring, no composite.

**D-43 Result.** Batters: the same ten players as the phase 3 build, in a different order. Bowlers: nine of
ten the same; Lockie Ferguson replaces Wanindu Hasaranga because recency decay was removed. Two designs
agreeing on the batter set is a robustness finding, not a tuning outcome.

**D-44 Which list is final.** V2 is the recommended submission, because every option behind it was chosen on
forward-in-time evidence with an overfitting guard and confirmed on trials it never saw. The phase 3 lists
remain available and are marked as superseded in `docs/FINDINGS.md`.

**D-45 Known limits.** Baselines, win probability and pressure flags are fitted on all matches, so rolling
trials still pass a little league-wide information backwards. It cannot favour a player. Rolling windows
overlap in their training data.

## K. V3: final model, from open-ended experiments on the V2 trials

Instruction: use any method to reach the best possible model. Same yardstick and trials as V2 (25 tuning,
22 confirmation). Adoption rule tightened: tuning paired z above 2 AND not worse on the confirmation trials.
All results in `outputs/v3/`.

**D-46 New engine.** `src/v3_lib.py` generalises the V2 ridge (verified identical to V2 at default settings,
difference below 1e-13). New options: leverage floor and cap, separate penalty for the wicket part of NRAE,
player-by-context interactions (pace or left-hander, death overs), separate opponent penalty, score
re-weighting and WPA blending, and ensembles of configurations.

**D-47 Round 1, structure (structure.csv).** Passed: bowlers, wicket part penalised 3x and 10x (10x best:
tuning +0.022, confirmation +0.027); batters, pace interaction with penalty 3,000 (tuning +0.010, z 2.2,
confirmation +0.006). Failed: every ensemble (all worse), leverage floors, opponent-penalty changes,
death-overs and left-hander interactions, other leverage powers and half-lives.

**D-48 Round 2, combinations (combine.csv).** Nothing passed on top of the round-1 winners. Near miss:
batter leverage cap 3 (positive on both trial sets, tuning z 1.2 and 1.5 in two rounds), not adopted.

**D-49 Round 3, score construction (score.csv, score_xfeat.csv).** Re-weighting the wicket part and blending
WPA did not pass for either group.

**D-50 Richer baseline.** Identity-free situational features added to the expected-runs and dismissal
models (momentum, dot streak, live win probability, ball in over, partnership length, bowler workload).
Accuracy gain is tiny (expected-runs RMSE down about 0.0015). In the trials it helps batters (tuning +0.0063
z 3.3 on the V2 model, +0.0053 z 2.1 on top of the pace term; confirmation positive) and hurts bowlers on
confirmation (-0.0032), so it is used for batters only, written to `bat_credit_v3.parquet` so earlier
results stay reproducible.

**D-51 Final configuration.** Batters: V2 settings + pace interaction (penalty 3,000) on the richer
baseline. Bowlers: V2 settings + wicket-part penalty 30,000 (10x). Paired against V2 on identical trials:
batters +0.015 tuning (z 3.4), +0.009 confirmation (z 2.0); bowlers +0.022 tuning (z 2.2), +0.027
confirmation (z 2.9).

**D-52 Bootstrap fix.** With the interaction term, a resample that dropped every match of a player divided
0 by 0 and ranked him last. The share now defaults to 0 so he keeps the prior, as in V2.

**D-53 Honest caveats.** About 30 variants were tried per group, so with a 2-SE rule one false positive is
plausible; the batter changes are the weaker ones. The leakage caveat of D-45 still applies to the trials
(not to the final model). V3 is the recommended submission; V2 and phase 3 remain as records.


## L. Review remediation (2026-11-13)

**D-54 V3 selection rule corrected.** Candidate adoption now uses tuning trials only (paired z > 2). The legacy 22 confirmation trials remain in the comparison tables as diagnostics, but are explicitly not an untouched holdout because prior V3 iterations used confirmation performance to gate candidates. No new untouched holdout can be manufactured from the already-used historical observations; a genuinely independent confirmation requires future matches or a newly collected dataset.

**D-55 RR fit rebuilt from V3.** The V3 pipeline now writes a separate RR fit under outputs/v3/rr_fit/, reading V3 batter and bowler ratings, V3 batter credit, and the existing bowler credit. The earlier phase-1 RR fit remains preserved for comparison. V3 schema differences (no grid-top-10 frequency and no separate final-rank column in the full ratings table) fall back to bootstrap top-10 probability and model rank.

**D-56 Objective stated precisely.** The V3 rating is leverage-weighted, opponent-adjusted NRAE per 100 balls with shrinkage. It estimates overall high-leverage performance relative to the identity-free baseline; it is not a causal within-player pressure uplift and does not optimise consistency. Raw pressure-minus-normal strike-rate/economy contrasts and pressure-innings NRAE dispersion are exposed as descriptive diagnostics, not ranking inputs. The prior tests of consistency and delta components remain documented in D-31 to D-35.

**D-57 Superseded: result-anchored targets removed.** Result-derived target reconstruction was removed from the state pipeline. The only chase target now used by WP, required-rate and pressure features is the rounded first-innings ball-data total plus one. The row-level audit contains no final innings total, result margin, wicket margin or winner-derived adjustment.

**D-58 Upstream features and rating validation made chronological.** The pipeline now uses a 20% chronological warm-up period, internally cross-fitted by match, followed by five forward-only folds. WP models, expected-value models, fold-specific outcome frequencies for leverage, pressure percentile references, resource/wicket values, venue averages, and ridge penalty CV use only warm-up or earlier-date data when scoring each later fold. The temporal validation stage then fits V3 on pre-cutoff matches and scores the next six/seven months. This is an end-to-end chronological feature-generation and rating-fit check after the warm-up period. The validation windows remain diagnostic rather than a pristine final holdout because V3 development has already examined overlapping historical periods; future matches are still needed for independent prospective confirmation.

**D-59 Initial Playing-XI anomaly audit.** The first remediation exported missing-striker ball-level aggregates and duplicate XI rows with match, player and team identifiers. Its pending-reconciliation status was superseded by the competition-roster cross-check in D-63. Raw source rows remain unchanged.

**D-60 Acceptance tests integrated.** run_all.py runs pytest after all stages and fails the pipeline if the acceptance suite fails. The standalone pytest command remains available for targeted reruns.


**D-61 Calibration audit and acceptance aligned.** After reviewing the first chronological out-of-fold calibration diagnostics, the documented acceptance tolerance was set to a maximum dense-bin gap no greater than 0.08 and no more than one bin outside its match-clustered 2-SD bootstrap band. The data-quality audit and acceptance tests now use the same gate. Raw bin gaps and uncertainty remain visible. This is a pragmatic diagnostic tolerance, not a statement of perfect calibration.

**D-62 Wicket expectation uses the validated simpler baseline.** The fold-calibrated LightGBM wicket classifier is retained as a diagnostic candidate. Player credit uses an innings-by-phase mean estimated from training matches only, because the prior out-of-fold classifier did not beat that identity-free reference on log loss. The baseline is cross-fitted by match and is therefore not contaminated by the scored fold.

**D-63 Audit outputs distinguish source omissions from pipeline defects.** Missing striker-to-XI references are cross-checked against the competition roster and expected delivery team. Duplicate XI memberships are deduplicated only for membership validation, while the raw duplicate rows remain available for inspection. Striker/non-striker identity collisions and bowlers exceeding 24 legal balls are exported as row-level diagnostics. Raw source files remain unchanged; no source record is silently fabricated or deleted.


**D-64 Verified ball-level batter identity correction.** Match 37086 (Afghanistan A vs Sri Lanka A, 18 October 2024), innings 1, delivery 111 (18.3), records Sharafuddin Ashraf as both striker and non-striker. Cricbuzz commentary records Zubaid Akbari's run-out at 17.5, then Ashraf batting with Shahidullah Kamal and facing the 18.3 delivery. The competition roster maps Shahidullah Kamal to player_id 3543. Stage 02 changes only the derived working copy's non-striker ID from 3550 to 3543, guarded by assertions on the raw values and exact delivery key. The raw CSV is unchanged. Evidence: https://www.cricbuzz.com/player-match-performance/match/107585/player/9854/batting?inningsId=1

**D-65 Expected-wicket calibration isolation.** The diagnostic LightGBM wicket classifier estimates its calibration map from a held-out subset of each training fold. The scored predictions now reuse the exact pilot estimator that generated those calibration scores; refitting on the full training fold would shift the score distribution and invalidate the map. When no calibrator can be estimated, the candidate is fit on the full training fold without a calibration map. Player credit continues to use the validated fold-local innings/phase mean baseline.


**D-66 Strictly past-only extras calibration.** The previous full-sample extras fit used winning margins from all clean matches to estimate the run value of each extra, then applied those values to earlier and later matches alike. This allowed future outcomes to influence historical match state. Stage 02 now estimates per-type values on clean run-margin matches from strictly earlier dates only; matches played on the same date share a parameter vintage. Before 40 prior calibration matches exist, it uses the fixed one-run-per-extra assumption. Every match's method, training count, latest training date and coefficients are exported to \`outputs/tables/extras_calibration_by_match.csv\`. The out-of-time margin comparison is diagnostic and does not use a same-match or future result to construct that match's feature values.


**D-67 Primary ranking restored to the pre-registered objective.** The delivered primary shortlist and RR fit use the original 0.40 Level, 0.25 Impact, 0.20 Consistency and 0.15 Delta composite, with the eligibility thresholds in `config.json`. The later Level-only V3 candidate is retained as a separate predictive challenger because it performed better on some held-out comparisons, but temporal evidence is mixed and its objective differs from the task brief. It no longer replaces the primary task ranking. The task-specific ranking and predictive challenger are reported separately.


**D-68 Win-probability calibration: prefer a smooth match-weighted mapping.** The first attempt to replace Platt with isotonic calibration produced excessive local variance in the probability tails on the regenerated run (log loss 0.590 versus 0.694 for the state-free baseline; several bins with 2,500 or more balls had absolute gaps above 0.18). The isotonic experiment was therefore rejected. The primary fold-local calibrator is match-weighted Platt scaling, fitted only on the held-out calibration matches within each fold. Every match contributes equal aggregate calibration weight; only a positive-slope mapping is accepted. Calibration remains measured on untouched scored folds. Acceptance checks now include material probability bins with at least 2,500 balls, not only bins above 5,000.

**D-69 V2 search score is applied by the final rating stage.** The search can select NRAE, WPA or one of its pre-defined NRAE/WPA blends using tuning-only evidence. The V2 rating stage previously asserted that the chosen score must be NRAE and then always ranked by NRAE, so a valid tuning choice such as `blend0.25` could stop execution or be silently misrepresented. The final stage and its match bootstrap now apply the exact selected score to the same eligible-player universe used to standardise blends; the exported table records both source components and the applied score name.


**D-70 Eligibility thresholds are never relaxed to satisfy a pool-size target.** The primary ranking uses the pressure balls, pressure innings/spells, total-ball and recency thresholds registered in `config.json`. If fewer than the configured minimum pool qualify, the pipeline stops and reports that conflict rather than silently lowering the thresholds. The exported ratings table and tests verify all included players against every registered threshold.


**D-71 V2/V3 model selection is forward-only.** The earlier V2 search mixed five chronological six-month windows with twenty random half-sample splits in both directions. The random splits could train on matches later than the test matches and were therefore unsuitable for selecting a model intended to predict future performance. They are removed from both V2 and V3 trial generation. V2 writes a row-level `validation_audit.csv` with train/test date boundaries and future-training counts; V3 trial files carry the same dates and a temporal flag. Acceptance tests require strictly increasing train/test chronology for every tuning and confirmation trial. Confirmation windows remain diagnostic and are not used for adoption.


**D-72 V2 search and final scoring use the same player universe.** The search previously required 40 leverage-weighted pressure units, whereas the final ranking required raw pressure deliveries, 150 total deliveries and a recent appearance. A selected blend was consequently standardised on a different set of players from the population used for deployment. V2 now uses one shared eligibility function for forward-window model selection and final ratings: raw pressure deliveries, total deliveries and the last two calendar years relative to each training cutoff. The final 2026 rating uses the same rule relative to its 2026-11-01 anchor. The audit records the eligible training population in each window, and tests compare the final IDs with the shared helper.


**D-73 V3 challenger uses the same eligibility in search and final ratings.** The challenger search previously defined training eligibility using leverage-weighted pressure units, while the published V3 ratings used raw pressure deliveries, total deliveries and recent appearance. The temporal candidate trials now use the shared V2 eligibility helper and the final V3 stage calls the same helper. Tests compare the published V3 player IDs with the helper's result for the final 2026-11-01 anchor.
