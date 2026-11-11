"""Robustness helpers: match bootstrap, split-half reliability, sensitivity configurations."""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import CFG, SEED
from ratings_lib import Prep, rate, composite, COMPONENTS

_G = {}


def _boot_one(i):
    prep, lam, elig, estimator = _G["prep"], _G["lam"], _G["elig"], _G["estimator"]
    rng = np.random.RandomState(SEED + 1000 + i)
    M = len(prep.matches)
    mult = np.bincount(rng.randint(0, M, M), minlength=M).astype(float)
    t = composite(rate(prep, lam[0], lam[1], mult), elig, estimator=estimator).sort_values("player_id")
    return t["rank"].values, t.rating.values, t.delta.values, t.level.values


def bootstrap(prep, lam, elig, n_boot, estimator="ridge", processes=4):
    """Cluster bootstrap by match with the eligible set held fixed. Returns arrays n_boot x n_eligible
    in ascending player_id order."""
    import multiprocessing as mp
    _G.update(prep=prep, lam=lam, elig=elig, estimator=estimator)
    ctx = mp.get_context("fork")
    with ctx.Pool(processes) as pool:
        res = pool.map(_boot_one, range(n_boot), chunksize=10)
    ids = np.sort(prep.players[elig])
    return ids, [np.array([r[j] for r in res]) for j in range(4)]


def split_half(df, role, lam, splits, pcol="pA", scale=0.5, estimator="ridge", weights=None,
               prep_kw=None, rate_fn=None, composite_fn=None):
    """Rate each half of the matches separately and correlate across halves.
    splits: list of boolean arrays over sorted unique match ids (True = half A).
    Eligibility in a half uses `scale` times the thresholds and drops the recent-appearance rule."""
    rate_fn = rate_fn or rate
    composite_fn = composite_fn or composite
    mids = np.sort(df.match_id.unique())
    rows = []
    for s, in_a in enumerate(splits):
        halves = []
        for part in (mids[in_a], mids[~in_a]):
            d = df[df.match_id.isin(part)]
            prep = Prep(d, role, pcol=pcol, **(prep_kw or {}))
            elig = prep.eligible(scale, require_recent=False)
            t = composite_fn(rate_fn(prep, lam[0], lam[1]), elig, weights=weights, estimator=estimator)
            halves.append(t.set_index("player_id"))
        a, b = halves
        common = a.index.intersection(b.index)
        r = dict(split=s, n_common=len(common))
        if len(common) >= 10:
            r["rating"] = spearmanr(a.loc[common, "rating"], b.loc[common, "rating"]).statistic
            for c in COMPONENTS:
                r[c] = spearmanr(a.loc[common, f"z_{c}"], b.loc[common, f"z_{c}"]).statistic
        rows.append(r)
    return pd.DataFrame(rows)


def random_splits(match_ids, n, seed=SEED):
    mids = np.sort(np.unique(match_ids))
    rng = np.random.RandomState(seed + 77)
    out = []
    for _ in range(n):
        perm = rng.permutation(len(mids))
        m = np.zeros(len(mids), bool)
        m[perm[: len(mids) // 2]] = True
        out.append(m)
    return out


def dirichlet_weights(n, seed=SEED):
    cw = CFG["composite_weights"]
    base = np.array([cw[c] for c in COMPONENTS])
    rng = np.random.RandomState(seed + 5)
    draws = rng.dirichlet(CFG["robustness"]["dirichlet_concentration"] * base, size=n)
    return np.vstack([base, draws])
