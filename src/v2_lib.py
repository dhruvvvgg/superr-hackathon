"""Version 2 rating engine: a leverage-weighted hierarchical ridge whose every design choice is picked by
how well it predicts FUTURE pressure performance (rolling forward-in-time origin).

fit() returns, per player, a shrunk estimate of NRAE per 100 balls and of WPA per 100 balls under the
requested weighting. It is cheap enough to call hundreds of times: the normal-equation matrix depends on
the weights only, so the NRAE and WPA solves share one factorisation.
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.linalg import cho_factor, cho_solve
from scipy.stats import rankdata

POS_GROUPS = [(0, 2, "open"), (3, 4, "mid"), (5, 11, "late")]


def _codes(x):
    u, inv = np.unique(np.asarray(x), return_inverse=True)
    return u, inv


def role_groups(df, role):
    """Main role of each player in the data given (modal batting-position group, or pace/spin x arm)."""
    if role == "bat":
        pos = df[df.faced == 1].groupby(["player_id", "match_id"]).batting_order.first().groupby("player_id").median()
        g = pd.cut(pos, [-1, 2, 4, 20], labels=["open", "mid", "late"]).astype(object)
    else:
        arm = df.bowling_type.str.startswith("Left").map({True: "L", False: "R"})
        key = df.pace_or_spin.str[0] + arm
        g = key.groupby(df.player_id).agg(lambda s: s.value_counts().index[0])
    return g


def fit(df, role, anchor, half_life=24.0, alpha=1.0, assoc_w=0.5, lam=3000.0, role_prior=True,
        opp_adjust=True, mult=None, lam_ctx_ratio=1.0, cap=10.0):
    """df: credit rows (one role). anchor: Timestamp the recency weights are measured back from.
    mult: optional per-match multiplicity array aligned with np.unique(df.match_id) (bootstrap)."""
    d = df
    n = len(d)
    months = (anchor - pd.to_datetime(d.match_date)).dt.days.values / 30.4375
    w = np.ones(n) if not half_life else 0.5 ** (months / half_life)
    w = w * np.where(d.w_comp.values < 1.0, assoc_w, 1.0)
    if alpha:
        w = w * np.clip(d.leverage.values.astype(float), 0.05, cap) ** alpha
    pl, pi = _codes(d.player_id.values)
    P = len(pl)
    if mult is not None:
        mu, mi = _codes(d.match_id.values)
        w = w * np.asarray(mult, dtype=float)[mi]
    w = w / w.mean()
    cols, rows, vals = [], [], []
    r = np.arange(n)
    blocks = {}
    col = 0
    # unpenalised: intercept, tier dummies, role-group dummies
    unp = [np.ones(n), (d.tier.values == "T20I").astype(float), (d.tier.values == "A-team").astype(float)]
    rg_names = []
    if role_prior:
        rg = role_groups(d, role)
        pg = pd.Series(rg).reindex(pl).fillna("mid" if role == "bat" else "PR").astype(str).values
        rg_names = sorted(set(pg))
        rowg = pg[pi]
        for name in rg_names[1:]:
            unp.append((rowg == name).astype(float))
    U = np.column_stack(unp)
    k_unp = U.shape[1]
    Xu = sp.csr_matrix(U)
    pen = [np.full(k_unp, 1e-6)]
    parts = [Xu]
    blocks["player"] = (k_unp, k_unp + P)
    parts.append(sp.csr_matrix((np.ones(n), (r, pi)), shape=(n, P)))
    pen.append(np.full(P, lam))
    col = k_unp + P
    ctx = [("ts", d.team_season.values), ("venue", d.venue_id.values)]
    if opp_adjust:
        ctx.insert(0, ("opp", d.opp_id.values))
    for name, v in ctx:
        u, inv = _codes(v)
        parts.append(sp.csr_matrix((np.ones(n), (r, inv)), shape=(n, len(u))))
        pen.append(np.full(len(u), lam * (1.0 if name == "opp" else lam_ctx_ratio)))
    X = sp.hstack(parts).tocsr()
    pen = np.concatenate(pen)
    Xw = X.multiply(w[:, None]).tocsr()
    G = (X.T @ Xw).toarray()
    G[np.diag_indices_from(G)] += pen
    ys = np.column_stack([d.nrae.values, d.wpa.values])
    rhs = np.asarray(X.T @ (w[:, None] * ys))
    beta = cho_solve(cho_factor(G, overwrite_a=True, check_finite=False), rhs, check_finite=False)
    a, b = blocks["player"]
    # player effect plus role-group mean, so the score is comparable across roles
    shift = np.zeros(P) if not role_prior else np.zeros((P, 2))
    out = beta[a:b]
    if role_prior:
        gcoef = np.vstack([np.zeros((1, 2)), beta[3:k_unp]])
        gi = {nme: i for i, nme in enumerate(rg_names)}
        out = out + gcoef[[gi[g] for g in pg]]
    res = pd.DataFrame({"player_id": pl, "s_nrae": 100 * out[:, 0], "s_wpa": 100 * out[:, 1]})
    return res


def wspearman(a, b, w):
    ra, rb = rankdata(a), rankdata(b)
    w = np.asarray(w, dtype=float) / np.sum(w)
    ma, mb = (w * ra).sum(), (w * rb).sum()
    c = (w * (ra - ma) * (rb - mb)).sum()
    den = np.sqrt((w * (ra - ma) ** 2).sum() * (w * (rb - mb) ** 2).sum())
    return c / den if den > 0 else np.nan


def pressure_stats(df, role, pcol="pA"):
    """Per player: pressure units (balls), pressure NRAE and WPA per 100 (w_comp weighted)."""
    d = df[df[pcol].astype(bool)]
    unit = (d.faced if role == "bat" else pd.Series(1.0, index=d.index)) * d.w_comp
    g = pd.DataFrame({"player_id": d.player_id, "unit": unit, "nrae": d.nrae * d.w_comp, "wpa": d.wpa * d.w_comp}) \
        .groupby("player_id").sum()
    g["nrae100"] = 100 * g.nrae / g.unit.replace(0, np.nan)
    g["wpa100"] = 100 * g.wpa / g.unit.replace(0, np.nan)
    return g


def eval_sets(tr, te, role, anchor, cfg, min_train=40, min_test=25, extra_scores=None):
    """Fit on `tr`, score on pressure performance in `te`. Returns weighted Spearman correlations (NRAE and
    WPA targets) for several score variants, and the number of players compared."""
    st_tr, st_te = pressure_stats(tr, role), pressure_stats(te, role)
    elig = st_tr[st_tr.unit >= min_train].index
    tg = st_te[st_te.unit >= min_test]
    common = elig.intersection(tg.index)
    out = {"n": len(common)}
    fitted = fit(tr, role, anchor, **cfg).set_index("player_id")
    scores = {"nrae": fitted.s_nrae, "wpa": fitted.s_wpa}
    zz = lambda x: (x - x.mean()) / x.std()
    base = fitted.loc[fitted.index.intersection(elig)]
    for beta in (0.25, 0.5, 1.0):
        scores[f"blend{beta:g}"] = zz(base.s_nrae) + beta * zz(base.s_wpa)
    for name, sc in (extra_scores(tr, role, st_tr) if extra_scores else {}).items():
        scores[name] = sc
    for sname, sc in scores.items():
        c = common.intersection(sc.dropna().index)
        ww = tg.loc[c, "unit"].values
        out[sname] = (wspearman(sc[c].values, tg.loc[c, "nrae100"].values, ww),
                      wspearman(sc[c].values, tg.loc[c, "wpa100"].values, ww))
    return out


def eval_fold(df, role, cutoff, months, cfg, **kw):
    cut = pd.Timestamp(cutoff)
    end = cut + pd.DateOffset(months=months)
    dd = pd.to_datetime(df.match_date)
    return eval_sets(df[dd < cut], df[(dd >= cut) & (dd < end)], role, cut, cfg, **kw)


def eval_split(df, role, train_ids, cfg, anchor, **kw):
    inn = df.match_id.isin(train_ids)
    return eval_sets(df[inn], df[~inn], role, anchor, cfg, **kw)
