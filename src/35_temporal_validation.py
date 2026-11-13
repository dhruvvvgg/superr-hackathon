"""Forward-only V3 rating diagnostics on chronologically cross-fit credit tables.

The pipeline now generates win-probability, leverage, pressure flags, resource values, expected-value
residuals, venue context and ridge-CV folds with chronological cross-fitting. The initial warm-up period
uses internal match-group cross-fitting; every later fold trains only on earlier dates. This report is
diagnostic and is not used for model selection.
"""
import json
import os

import numpy as np
import pandas as pd

from common import PROCESSED, ROOT
from v2_lib import pressure_stats, wspearman
from v3_lib import fit3

OUT = os.path.join(ROOT, "outputs", "v3")
CUTS = [
    ("2023-04-01", 6), ("2023-10-01", 6), ("2024-04-01", 6),
    ("2024-10-01", 6), ("2025-04-01", 6), ("2025-10-01", 6),
    ("2026-04-01", 7),
]


def evaluate(role, credit_file, cfg):
    d = pd.read_parquet(os.path.join(PROCESSED, credit_file))
    dates = pd.to_datetime(d.match_date)
    rows = []
    for cut_text, months in CUTS:
        cut = pd.Timestamp(cut_text)
        end = cut + pd.DateOffset(months=months)
        tr = d[dates < cut]
        te = d[(dates >= cut) & (dates < end)]
        if tr.empty or te.empty:
            continue
        train_dates = pd.to_datetime(tr.match_date)
        test_dates = pd.to_datetime(te.match_date)
        assert train_dates.max() < test_dates.min(), "temporal split contains future training data"
        fitted = fit3(tr, role, cut, **cfg).set_index("player_id").s_nrae
        train_stats = pressure_stats(tr, role)
        test_stats = pressure_stats(te, role)
        eligible = train_stats[train_stats.unit >= 40].index
        test_eligible = test_stats[test_stats.unit >= 20].index
        common = fitted.index.intersection(eligible).intersection(test_eligible)
        if len(common) >= 5:
            w = test_stats.loc[common, "unit"].to_numpy(dtype=float)
            c_nrae = wspearman(fitted.loc[common].to_numpy(), test_stats.loc[common, "nrae100"].to_numpy(), w)
            c_wpa = wspearman(fitted.loc[common].to_numpy(), test_stats.loc[common, "wpa100"].to_numpy(), w)
            objective = 0.5 * (c_nrae + c_wpa)
        else:
            c_nrae = c_wpa = objective = np.nan
        rows.append(dict(
            role=role, cutoff=cut_text, test_end=end.date().isoformat(),
            n_train_matches=int(tr.match_id.nunique()), n_test_matches=int(te.match_id.nunique()),
            n_players=len(common), nrae_corr=c_nrae, wpa_corr=c_wpa, objective=objective,
            train_max_date=train_dates.max().date().isoformat(),
            test_min_date=test_dates.min().date().isoformat(),
            future_train_matches=int((train_dates >= test_dates.min()).sum()),
            upstream_temporal_status="chronologically_crossfit",
        ))
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    chosen = json.load(open(os.path.join(OUT, "chosen_config.json"), encoding="utf-8"))
    rows = []
    for role, file in [("bat", "bat_credit_v3.parquet"), ("bowl", "bowl_credit.parquet")]:
        cfg = {k: v for k, v in chosen[role].items() if k not in ("credit", "evidence")}
        rows.extend(evaluate(role, file, cfg))
    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("No temporal validation windows had both training and test observations")
    out.to_csv(os.path.join(OUT, "temporal_validation.csv"), index=False, float_format="%.6g")
    print(out.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
