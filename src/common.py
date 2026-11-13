"""Shared paths, config, loaders and small helpers used by every stage."""
import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
# SUPERR_TAG redirects every derived file to a side directory so that phase 2 experiments never
# overwrite the main outputs. SUPERR_OVERRIDES is a JSON dict of dotted config keys.
TAG = os.environ.get("SUPERR_TAG", "")
if TAG:
    INTERIM = os.path.join(ROOT, "data", "experiments", TAG, "interim")
    PROCESSED = os.path.join(ROOT, "data", "experiments", TAG, "processed")
    TABLES = os.path.join(ROOT, "data", "experiments", TAG, "tables")
    FIGURES = os.path.join(ROOT, "data", "experiments", TAG, "figures")
else:
    INTERIM = os.path.join(ROOT, "data", "interim")
    PROCESSED = os.path.join(ROOT, "data", "processed")
    TABLES = os.path.join(ROOT, "outputs", "tables")
    FIGURES = os.path.join(ROOT, "outputs", "figures")
for _d in (INTERIM, PROCESSED, TABLES, FIGURES):
    os.makedirs(_d, exist_ok=True)


def load_config():
    with open(os.path.join(ROOT, "config.json")) as f:
        cfg = json.load(f)
    for key, value in json.loads(os.environ.get("SUPERR_OVERRIDES", "{}")).items():
        node = cfg
        parts = key.split(".")
        for part in parts[:-1]:
            node = node[part]
        node[parts[-1]] = value
    return cfg


CFG = load_config()
SEED = CFG["seed"]


def temporal_fold_map(match_ids, match_dates, n_warmup_folds=5, n_test_folds=5, seed=SEED):
    """Warm-up cross-fit folds followed by forward-only chronological test folds."""
    m = pd.DataFrame({"match_id": np.asarray(match_ids), "match_date": pd.to_datetime(match_dates)})
    m = m.drop_duplicates("match_id").sort_values(["match_date", "match_id"])
    dates = np.sort(m.match_date.dt.normalize().unique())
    if len(dates) <= n_test_folds:
        raise ValueError("Not enough distinct match dates for chronological folds")
    n_warm_dates = max(1, min(len(dates) - n_test_folds, int(np.ceil(len(dates) * 0.20))))
    warm_dates, future_dates = dates[:n_warm_dates], dates[n_warm_dates:]
    warm_ids = m.loc[m.match_date.dt.normalize().isin(warm_dates), "match_id"].to_numpy()
    rng = np.random.RandomState(seed)
    perm = rng.permutation(warm_ids)
    out = {mid: -n_warmup_folds + (i % n_warmup_folds) for i, mid in enumerate(perm)}
    for k, date_group in enumerate(np.array_split(future_dates, n_test_folds)):
        ids = m.loc[m.match_date.dt.normalize().isin(date_group), "match_id"].to_numpy()
        out.update({mid: k for mid in ids})
    return out


def train_mask_for_fold(fold, fold_id):
    """Warm-up folds cross-fit against warm-up peers; later folds train on prior folds only."""
    fold = np.asarray(fold)
    return ((fold < 0) & (fold != fold_id)) if fold_id < 0 else (fold < fold_id)


def raw(name):
    return pd.read_csv(os.path.join(RAW, f"{name}.csv"), low_memory=False)


def checked_merge(left, right, label, **kw):
    """Merge that prints row counts before and after and refuses to change the row count
    of the left table unless explicitly allowed (how='inner' with allow_drop=True)."""
    allow_drop = kw.pop("allow_drop", False)
    n0 = len(left)
    out = left.merge(right, **kw)
    print(f"  [merge] {label}: left={n0} right={len(right)} -> {len(out)}")
    if len(out) > n0:
        raise AssertionError(f"merge '{label}' duplicated rows: {n0} -> {len(out)}")
    if len(out) < n0 and not allow_drop:
        raise AssertionError(f"merge '{label}' dropped rows: {n0} -> {len(out)}")
    return out


_RES = re.compile(r"(\d+)\s*(run|wicket|wkt)", re.I)


def parse_result(result):
    """Return (kind, n, flags) from a free-text result string.
    kind is 'runs', 'wkts', 'tie', 'none' (abandoned or no result) or 'other'."""
    r = str(result)
    low = r.lower()
    dls = bool(re.search(r"d/l|dls", low))
    superover = bool(re.search(r"super\s*over|eliminator|tied", low))
    if "abandon" in low or "no result" in low:
        return "none", np.nan, dls, superover
    if superover:
        return "tie", np.nan, dls, superover
    m = _RES.search(r)
    if not m:
        return "other", np.nan, dls, superover
    kind = "runs" if m.group(2).lower() == "run" else "wkts"
    return kind, int(m.group(1)), dls, superover


def player_names():
    """player_id -> player_name, asserted one name per id."""
    mp = raw("competition_team_player_mapping")
    g = mp.groupby("player_id").player_name.nunique()
    assert (g == 1).all(), "a player_id maps to more than one name"
    return mp.drop_duplicates("player_id").set_index("player_id").player_name


def phase_of_over(over):
    over = np.asarray(over)
    return np.where(over <= 6, "powerplay", np.where(over <= 15, "middle", "death"))


def save_table(df, name, index=False):
    path = os.path.join(TABLES, name)
    df.to_csv(path, index=index, float_format="%.6g")
    print(f"  wrote outputs/tables/{name} ({len(df)} rows)")


def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "font.size": 12, "axes.titlesize": 14, "axes.labelsize": 12, "figure.dpi": 110,
        "savefig.dpi": 160, "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
        "axes.spines.right": False,
    })
    return plt
