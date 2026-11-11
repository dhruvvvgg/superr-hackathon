"""Shared paths, config, loaders and small helpers used by every stage."""
import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
INTERIM = os.path.join(ROOT, "data", "interim")
PROCESSED = os.path.join(ROOT, "data", "processed")
TABLES = os.path.join(ROOT, "outputs", "tables")
FIGURES = os.path.join(ROOT, "outputs", "figures")
for _d in (INTERIM, PROCESSED, TABLES, FIGURES):
    os.makedirs(_d, exist_ok=True)


def load_config():
    with open(os.path.join(ROOT, "config.json")) as f:
        return json.load(f)


CFG = load_config()
SEED = CFG["seed"]


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
