"""V3 rating engine: generalises the V2 leverage-weighted ridge with options that can only be judged by
prediction.

New options (all default to V2 behaviour):
  floor        lower clip of the leverage weight (V2: 0.05). A higher floor keeps more information from
               ordinary balls.
  lam_wkt      separate ridge penalty for the wicket part of NRAE (V2: same penalty, one outcome). The
               rating is the sum of the separately shrunk runs part and wicket part.
  inter        player-by-context interaction, shrunk with its own penalty `lam_inter`:
               batters "pace" (ball from a pace bowler), bowlers "lhb" (left-handed batter), both "death".
               The rating adds the interaction weighted by the player's own share of that context.
  lam_opp      separate penalty for the opponent block (V2: same as lam).
fit3 returns per player: s_runs, s_wkt, s_nrae (= sum), s_wpa, all per 100 balls.
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.linalg import cho_factor, cho_solve


def _codes(x):
    u, inv = np.unique(np.asarray(x), return_inverse=True)
    return u, inv


def weights(d, anchor, half_life=24.0, alpha=1.0, assoc_w=0.5, floor=0.05, cap=10.0, mult=None):
    months = (anchor - pd.to_datetime(d.match_date)).dt.days.values / 30.4375
    w = np.ones(len(d)) if not half_life else 0.5 ** (months / half_life)
    w = w * np.where(d.w_comp.values < 1.0, assoc_w, 1.0)
    if alpha:
        w = w * np.clip(d.leverage.values.astype(float), floor, cap) ** alpha
    if mult is not None:
        _, mi = _codes(d.match_id.values)
        w = w * np.asarray(mult, dtype=float)[mi]
    return w / w.mean()


def context_flag(d, role, inter):
    if inter == "pace":
        return (d.pace_or_spin.values == "Pace").astype(float)
    if inter == "lhb":
        return (d.batting_type.values == "LHB").astype(float)
    if inter == "death":
        return (d.phase.values == "death").astype(float)
    raise ValueError(inter)


def fit3(df, role, anchor, half_life=24.0, alpha=1.0, assoc_w=0.5, lam=3000.0, floor=0.05, cap=10.0,
         lam_wkt=None, inter=None, lam_inter=None, lam_opp=None, opp_adjust=True, mult=None, **_):
    d = df
    n = len(d)
    w = weights(d, anchor, half_life, alpha, assoc_w, floor, cap, mult)
    pl, pi = _codes(d.player_id.values)
    P = len(pl)
    r = np.arange(n)
    U = np.column_stack([np.ones(n), (d.tier.values == "T20I").astype(float), (d.tier.values == "A-team").astype(float)])
    k0 = U.shape[1]
    parts = [sp.csr_matrix(U), sp.csr_matrix((np.ones(n), (r, pi)), shape=(n, P))]
    blocks = [("unp", k0), ("player", P)]
    flag = None
    if inter:
        flag = context_flag(d, role, inter)
        U2 = np.column_stack([flag])               # unpenalised main effect of the context
        parts.append(sp.csr_matrix(U2)); blocks.append(("ctx_main", 1))
        m = flag > 0
        parts.append(sp.csr_matrix((np.ones(int(m.sum())), (r[m], pi[m])), shape=(n, P))); blocks.append(("inter", P))
    ctx = [("ts", d.team_season.values), ("venue", d.venue_id.values)]
    if opp_adjust:
        ctx.insert(0, ("opp", d.opp_id.values))
    for name, v in ctx:
        u, inv = _codes(v)
        parts.append(sp.csr_matrix((np.ones(n), (r, inv)), shape=(n, len(u)))); blocks.append((name, len(u)))
    X = sp.hstack(parts).tocsr()
    off, o = {}, 0
    for name, k in blocks:
        off[name] = (o, o + k); o += k
    G0 = (X.T @ X.multiply(w[:, None]).tocsr()).toarray()

    def penalty(lp):
        pen = np.full(X.shape[1], 1e-6)
        for name, (a, b) in off.items():
            if name in ("unp", "ctx_main"):
                continue
            lamv = {"player": lp, "inter": lam_inter or lp, "opp": lam_opp or lp}.get(name, lp)
            pen[a:b] = lamv
        return pen

    def solve(lp, ys):
        G = G0.copy()
        G[np.diag_indices_from(G)] += penalty(lp)
        rhs = np.asarray(X.T @ (w[:, None] * ys))
        return cho_solve(cho_factor(G, overwrite_a=True, check_finite=False), rhs, check_finite=False)

    a, b = off["player"]
    if lam_wkt is None:
        beta = solve(lam, np.column_stack([d.nrae_runs.values, d.nrae_wkt.values, d.wpa.values]))
        eff = beta[a:b]
        ib = beta[off["inter"][0]:off["inter"][1]] if inter else None
    else:
        b1 = solve(lam, np.column_stack([d.nrae_runs.values, d.wpa.values]))
        b2 = solve(lam_wkt, d.nrae_wkt.values[:, None])
        eff = np.column_stack([b1[a:b, 0], b2[a:b, 0], b1[a:b, 1]])
        if inter:
            ia, ibb = off["inter"]
            ib = np.column_stack([b1[ia:ibb, 0], b2[ia:ibb, 0], b1[ia:ibb, 1]])
        else:
            ib = None
    if inter:
        # player's own share of the context in leverage-weighted balls
        num = np.bincount(pi, w * flag, minlength=P)
        den = np.bincount(pi, w, minlength=P)
        share = np.divide(num, den, out=np.zeros(P), where=den > 0)   # a player absent from a resample keeps the prior
        cm = 0.0
        eff = eff + share[:, None] * ib
    out = pd.DataFrame({"player_id": pl, "s_runs": 100 * eff[:, 0], "s_wkt": 100 * eff[:, 1], "s_wpa": 100 * eff[:, 2]})
    out["s_nrae"] = out.s_runs + out.s_wkt
    return out
