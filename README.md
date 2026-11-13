# SupeRR Selector Season 2: pressure-player model for Rajasthan Royals

A reproducible pipeline that defines pressure in T20 cricket from win-probability leverage, measures how
batters and bowlers perform under it relative to an identity-free baseline, and ranks the most reliable
players. The recommended final answer is `docs/V3_FINDINGS.md` (outputs in `outputs/v3/`). `docs/V2_FINDINGS.md` records the intermediate redesign. `docs/FINDINGS.md` is the full record of data preparation, validation and the earlier ratings. Every decision is logged in `docs/DECISIONS.md`.

## Run

```bash
pip install -r requirements.txt
```

```bash
python run_all.py
```

```bash
python -m pytest -q tests
```

`run_all.py` runs every stage from the raw CSVs and then executes `python -m pytest -q tests` as the final
acceptance gate. It accepts a first stage, for example `python run_all.py 07`, to resume. All seeds are fixed
in `config.json`; deterministic outputs should be compared on the same dependency/platform versions.

The phase 2 model comparisons are not part of `run_all.py` because they take about 40 minutes:

```bash
python src/phase2_experiments.py
```

## Layout

```
config.json                 every tunable choice: weights, thresholds, grids, seeds
run_all.py                  runs stages 01 to 11 in order
src/01_profile.py           re-verifies the data facts, writes data_quality.csv
src/02_build_state.py       legal balls, extras calibration, targets, match state
src/03_win_prob.py          out-of-fold win-probability model and calibration
src/04_pressure.py          leverage, pressure score, tiers, variants, validation
src/05_expected.py          identity-free expected runs and wickets, wicket value
src/06_attribution.py       ball-level credit (NRAE and WPA) for batters and bowlers
src/07_ratings.py           ridge and empirical Bayes estimates, consistency, composite
src/08_robustness.py        bootstrap, sensitivity grid, persistence, decision rule, final lists
src/09_rr_fit.py            Rajasthan Royals profile, gap analysis and auction shortlist
src/10_audit.py             scorecard and integrity audit
src/12_improve.py           phase 3: candidate ratings scored on held-out predictive validity
src/13_improve2.py          phase 3: focused candidates, paired comparisons, temporal holdout
src/20_v2_search.py         V2: pick rating options by forward-in-time prediction (2-standard-error rule)
src/21_v2_rate.py           V2: final ratings and bootstrap intervals (outputs/v2/)
src/22_v2_report.py         V2: figures and docs/V2_FINDINGS.md
src/31_v3_credit.py         V3: richer situational baseline for batters (own credit file)
src/30_v3_experiments.py    V3: structural experiments on the held-out trials (all rounds)
src/32_v3_rate.py           V3: final ratings and bootstrap intervals (outputs/v3/)
src/33_v3_report.py         V3: final comparison, figures and docs/V3_FINDINGS.md
src/34_v3_rr_fit.py         V3: RR fit using V3 ratings and V3 batter credit
src/35_temporal_validation.py V3: forward-only rating-fit diagnostics on existing credit tables
src/v3_lib.py               V3 rating engine (separate wicket shrinkage, interaction terms)
src/11_report.py            writes docs/FINDINGS.md from the output tables
src/phase2_experiments.py   side-by-side model variants scored on model quality
src/*_lib.py, common.py     shared code
tests/                      acceptance checks and leakage guards
outputs/tables, figures     everything FINDINGS.md cites
outputs/phase1/, phase2/      earlier results (pre-audit, and after the role-aware baseline), kept for comparison
outputs/v3/rr_fit/             RR incumbent/gap/shortlist analysis using V3 ratings
outputs/v3/temporal_validation.csv  forward-only rating-fit diagnostics (upstream features remain non-temporal)
context/rr_auction_context.md   public context with source tags
```

## Data notes

- The six CSVs sit unchanged in `data/raw/`. They arrived with plain names, so no renaming was needed.
- `outputs/v3/rr_fit/` is the current RR fit layer; the earlier outputs/tables/rr_fit.csv is retained as the pre-V3 comparison.
- `outputs/tables/playing_eleven_missing_strikers.csv` and playing_eleven_duplicates.csv drill down the XI anomalies; they are reported, not silently corrected.
- `outputs/tables/target_reconstruction_audit.csv` documents how the result-anchored target differs from first-innings reconstruction.
- `docs/problem_statement.pdf` is the Round 1 brief. `CLAUDE_CODE_HANDOVER.md` is the build specification.
- `context/rr_auction_context.md` was supplied after the first build (public web research dated
  2026-11-11) and extended with facts derived from the CSVs. Everything not listed there is unverified.
- Three facts differ from the build specification and are documented in `docs/DECISIONS.md`: "other"
  extras are no-balls and are not legal deliveries (D-02); four DLS matches carry no revised-overs flag
  (D-04); the reconstructed chase target is replaced by a result-anchored target (D-07).
- Derived data in `data/interim/` and `data/processed/` is regenerated by the pipeline and is not
  committed.

## AI-use disclosure

The code and documents in this repository were produced with the help of an AI coding assistant working
from the written build specification. All numbers come from running the code on the supplied data.
