"""Rating engine shared by stages 07 (primary ratings), 08 (robustness) and 09 (RR fit).

A Prep object indexes one credit table (batters or bowlers) for one pressure definition and one
data subset. rate() turns it into per-player components; composite() z-scores and combines them.
Everything in rate() is vectorised so the match bootstrap can call it a thousand times.
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.linalg import cho_factor, cho_solve

from common import CFG

COMPONENTS = ["level", "impact", "consistency", "delta"]


def _codes(values):
    u, inv = np.unique(np.asarray(values), return_inverse=True)
    return u, inv


class Prep:
    def __init__(self, df, role, pcol="pA", use_recency=True, use_comp_weight=True):
        self.role = role
        self.pcol = pcol
        d = df.reset_index(drop=True)
        self.n = len(d)
        self.players, self.pi = _codes(d.player_id.values)
        self.opps, self.oi = _codes(d.opp_id.values)
        self.tss, self.ti = _codes(d.team_season.values)
        self.venues, self.vi = _codes(d.venue_id.values)
        self.use_ots = bool(CFG["ridge"].get("opp_team_season")) and "opp_team_season" in d
        if self.use_ots:
            self.otss, self.oti = _codes(d.opp_team_season.values)
        self.matches, self.mi = _codes(d.match_id.values)
        self.P = len(self.players)
        self.press = d[pcol].values.astype(bool)
        self.unit = d.faced.values.astype(float) if role == "bat" else np.ones(self.n)
        self.y = d.nrae.values.astype(float)
        self.wpa = d.wpa.values.astype(float)
        self.fold = d.fold.values.astype(int)
        w = np.ones(self.n)
        if use_recency:
            w = w * d.w_recency.values
        if use_comp_weight:
            w = w * d.w_comp.values
        self.w0 = w
        self.tier_t20i = (d.tier.values == "T20I").astype(float)
        self.tier_a = (d.tier.values == "A-team").astype(float)
        self._design()
        self._groups(d)
        self._counts(d)

    # ---- ridge design --------------------------------------------------------------------------
    def _design(self):
        n, P = self.n, self.P
        self.off = {}
        col = 4
        groups = [("player", P), ("delta", P), ("opp", len(self.opps)), ("ts", len(self.tss)),
                  ("venue", len(self.venues))]
        if self.use_ots:
            groups.append(("ots", len(self.otss)))
        for name, size in groups:
            self.off[name] = (col, col + size)
            col += size
        self.K = col
        r = np.arange(n)
        rows = [r, r, r, r, r, r[self.press], r, r, r]
        cols = [np.zeros(n, int), np.ones(n, int), np.full(n, 2), np.full(n, 3),
                self.off["player"][0] + self.pi, self.off["delta"][0] + self.pi[self.press],
                self.off["opp"][0] + self.oi, self.off["ts"][0] + self.ti, self.off["venue"][0] + self.vi]
        vals = [np.ones(n), self.press.astype(float), self.tier_t20i, self.tier_a, np.ones(n),
                np.ones(int(self.press.sum())), np.ones(n), np.ones(n), np.ones(n)]
        if self.use_ots:
            rows.append(r); cols.append(self.off["ots"][0] + self.oti); vals.append(np.ones(n))
        self.X = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                               shape=(n, self.K))

    def penalty(self, lam_main, lam_delta):
        pen = np.full(self.K, 1e-6)
        ratio = CFG["ridge"]["lambda_nuisance_ratio"]
        for name, lam in [("player", lam_main), ("delta", lam_delta), ("opp", lam_main),
                          ("ts", lam_main * ratio), ("venue", lam_main * ratio), ("ots", lam_main * ratio)]:
            if name not in self.off:
                continue
            a, b = self.off[name]
            pen[a:b] = lam
        return pen

    def gram(self, w, rows=None):
        X = self.X if rows is None else self.X[rows]
        ww = w if rows is None else w[rows]
        yy = self.y if rows is None else self.y[rows]
        Xw = X.multiply(ww[:, None]).tocsr()
        return (X.T @ Xw).toarray(), np.asarray(X.T @ (ww * yy)).ravel()

    def ridge(self, w, lam_main, lam_delta):
        G, c = self.gram(w)
        G[np.diag_indices_from(G)] += self.penalty(lam_main, lam_delta)
        beta = cho_solve(cho_factor(G, overwrite_a=True, check_finite=False), c, check_finite=False)
        a, b = self.off["player"]
        a2, b2 = self.off["delta"]
        e = self.y - self.X @ beta
        self.sigma2 = float(np.sum(w * e * e) / max(w.sum(), 1e-9))     # residual variance per unit weight
        return beta[a:b], beta[a2:b2], beta

    def cv_lambdas(self, grid_main=None, grid_delta=None):
        """5-fold CV grouped by match (the win-probability folds). Returns best pair and the table."""
        grid_main = grid_main or CFG["ridge"]["lambda_main_grid"]
        grid_delta = grid_delta or CFG["ridge"]["lambda_delta_grid"]
        w = self.w0
        G_all, c_all = self.gram(w)
        folds = sorted(np.unique(self.fold))
        parts = {}
        for k in folds:
            rows = np.where(self.fold == k)[0]
            parts[k] = (rows,) + self.gram(w, rows)
        res = []
        for lm in grid_main:
            for ld in grid_delta:
                pen = self.penalty(lm, ld)
                sse, sw = 0.0, 0.0
                for k in folds:
                    rows, Gk, ck = parts[k]
                    A = G_all - Gk
                    A[np.diag_indices_from(A)] += pen
                    beta = cho_solve(cho_factor(A, overwrite_a=True, check_finite=False), c_all - ck,
                                     check_finite=False)
                    e = self.y[rows] - self.X[rows] @ beta
                    sse += float(np.sum(w[rows] * e * e))
                    sw += float(w[rows].sum())
                res.append(dict(lambda_main=lm, lambda_delta=ld, cv_wmse=sse / sw))
        tab = pd.DataFrame(res)
        # reference: no player or context terms at all (intercept, pressure flag, tier only)
        sse, sw = 0.0, 0.0
        Z = self.X[:, :4].toarray()
        for k in folds:
            te = self.fold == k
            tr = ~te
            A = (Z[tr] * w[tr, None]).T @ Z[tr] + 1e-6 * np.eye(4)
            beta = np.linalg.solve(A, (Z[tr] * w[tr, None]).T @ self.y[tr])
            e = self.y[te] - Z[te] @ beta
            sse += float(np.sum(w[te] * e * e)); sw += float(w[te].sum())
        tab["cv_wmse_no_player_terms"] = sse / sw
        best = tab.loc[tab.cv_wmse.idxmin()]
        return float(best.lambda_main), float(best.lambda_delta), tab

    # ---- grouped sums for empirical Bayes and consistency -------------------------------------------
    def _groups(self, d):
        P = self.P
        key = self.pi.astype(np.int64) * (len(self.matches) + 1) + self.mi
        self.pm = {}
        for name, msk in [("press", self.press), ("normal", ~self.press)]:
            u, inv = np.unique(key[msk], return_inverse=True)
            g = dict(player=(u // (len(self.matches) + 1)).astype(int), match=(u % (len(self.matches) + 1)).astype(int))
            w = self.w0[msk]
            g["S_y"] = np.bincount(inv, w * self.y[msk], minlength=len(u))
            g["S_wpa"] = np.bincount(inv, w * self.wpa[msk], minlength=len(u))
            g["N"] = np.bincount(inv, w * self.unit[msk], minlength=len(u))
            self.pm[name] = g
        # pressure innings (batters) or pressure spells (bowlers): player x match x innings
        inn = d.innings.values
        m = self.press
        k2 = key[m] * 3 + inn[m]
        u, inv = np.unique(k2, return_inverse=True)
        s_y = np.bincount(inv, self.y[m], minlength=len(u))
        n_u = np.bincount(inv, self.unit[m], minlength=len(u))
        w_i = np.bincount(inv, self.w0[m], minlength=len(u)) / np.maximum(np.bincount(inv, minlength=len(u)), 1)
        pl = ((u // 3) // (len(self.matches) + 1)).astype(int)
        mt = ((u // 3) % (len(self.matches) + 1)).astype(int)
        if self.role == "bat":
            runs = np.bincount(inv, d.runs.values[m].astype(float), minlength=len(u))
            out = np.bincount(inv, d.out.values[m].astype(float), minlength=len(u)) > 0
            bad = out & (n_u <= 3) & (runs < 3)
            valid = np.ones(len(u), bool)
        else:
            exc = np.bincount(inv, (d.bowler_runs.values - d.x_runs.values)[m], minlength=len(u))
            bad = (exc / np.maximum(n_u, 1)) > 2.0
            valid = n_u > 0
        self.inn = dict(player=pl[valid], match=mt[valid], hit=(s_y >= 0).astype(float)[valid],
                        bad=bad.astype(float)[valid], w=w_i[valid], s_y=s_y[valid], n=n_u[valid])

    def _counts(self, d):
        P = self.P
        faced = self.unit > 0
        self.n_press = np.bincount(self.pi[self.press & faced], minlength=P)
        self.n_total = np.bincount(self.pi[faced], minlength=P)
        self.n_press_inn = np.bincount(self.inn["player"], minlength=P)
        recent = np.isin(d.year.values, CFG["eligibility"]["recent_years"]) & faced
        self.recent = np.bincount(self.pi[recent], minlength=P) > 0
        self.n_matches = np.bincount(np.unique(np.c_[self.pi[faced], self.mi[faced]], axis=0)[:, 0], minlength=P)

    def eligible(self, scale=1.0, require_recent=True):
        e = CFG["eligibility"]
        pre = "bat" if self.role == "bat" else "bowl"
        nb = e[f"{pre}_min_pressure_balls"] * scale
        ni = e[f"{pre}_min_pressure_{'innings' if pre == 'bat' else 'spells'}"] * scale
        return ((self.n_press >= nb) & (self.n_press_inn >= ni) & (self.n_total >= e["min_total_balls"] * scale)
                & (self.recent if require_recent else True))


# ---- empirical Bayes helpers ---------------------------------------------------------------------------
def _cluster_mean(g, key, k, P):
    """Weighted mean per player and its match-clustered variance. k = match multiplicities."""
    km = k[g["match"]]
    S = np.bincount(g["player"], km * g[key], minlength=P)
    N = np.bincount(g["player"], km * g["N"], minlength=P)
    M = np.bincount(g["player"], km * (g["N"] > 0), minlength=P)
    mean = np.where(N > 0, S / np.maximum(N, 1e-12), np.nan)
    r = g[key] - mean[g["player"]] * g["N"]
    var = np.bincount(g["player"], km * r * r, minlength=P) / np.maximum(N, 1e-12) ** 2
    var = np.where(M > 1, var * M / np.maximum(M - 1, 1), np.inf)
    return mean, var, N


def _eb(mean, var, pool):
    """Normal-normal shrinkage with method-of-moments prior variance, estimated on `pool`."""
    ok = pool & np.isfinite(mean) & np.isfinite(var) & (var > 0)
    if ok.sum() < 5:
        return np.zeros_like(mean), 0.0, 0.0
    m, v = mean[ok], var[ok]
    tau2 = max(np.var(m) - np.mean(v), 0.0)
    mu = np.mean(m)
    for _ in range(5):
        wi = 1.0 / (v + tau2)
        mu = np.sum(wi * m) / np.sum(wi)
        tau2 = max(np.sum(wi * ((m - mu) ** 2 - v)) / np.sum(wi), 0.0)
    shrink = np.where(np.isfinite(var), tau2 / (tau2 + np.where(np.isfinite(var), var, 1.0)), 0.0)
    est = mu + shrink * (np.where(np.isfinite(mean), mean, mu) - mu)
    return est, mu, tau2


def _beta_shrink(H, N, pool):
    ok = pool & (N > 0)
    if ok.sum() < 5:
        return np.full_like(H, np.nan), np.nan, np.nan
    r = H[ok] / N[ok]
    m = H[ok].sum() / N[ok].sum()
    v = np.average((r - m) ** 2, weights=N[ok])
    within = np.average(m * (1 - m) / N[ok], weights=N[ok])
    between = max(v - within, 1e-6)
    ab = float(np.clip(m * (1 - m) / between - 1.0, 2.0, 500.0))
    return (H + m * ab) / (N + ab), m, ab


def _beta_sd(m, ab):
    return float(np.sqrt(max(m * (1 - m), 0.0) / (ab + 1.0))) if np.isfinite(ab) else 0.0


def rate(prep, lam_main, lam_delta, mult=None):
    """Per-player components. mult: optional per-match multiplicities (bootstrap)."""
    P = prep.P
    k = np.ones(len(prep.matches)) if mult is None else np.asarray(mult, dtype=float)
    w = prep.w0 * k[prep.mi]
    normal, delta, _ = prep.ridge(w, lam_main, lam_delta)
    out = pd.DataFrame({"player_id": prep.players})
    out["normal"] = 100 * normal
    out["delta"] = 100 * delta
    out["level"] = out.normal + out.delta

    pool = prep.n_press >= 30
    gp, gn = prep.pm["press"], prep.pm["normal"]
    m_p, v_p, N_p = _cluster_mean(gp, "S_y", k, P)
    m_n, v_n, _ = _cluster_mean(gn, "S_y", k, P)
    out["raw_press_nrae100"] = 100 * m_p
    out["raw_normal_nrae100"] = 100 * m_n
    prior = dict(level=100 * np.sqrt(prep.sigma2 / lam_main + prep.sigma2 / lam_delta),
                 delta=100 * np.sqrt(prep.sigma2 / lam_delta))
    lev_eb, mu_l, tau_l = _eb(100 * m_p, 1e4 * v_p, pool)
    out["level_eb"] = lev_eb - mu_l
    d_eb, mu_d, tau_d = _eb(100 * (m_p - m_n), 1e4 * (v_p + v_n), pool)
    prior["level_eb"], prior["delta_eb"] = float(np.sqrt(tau_l)), float(np.sqrt(tau_d))
    out["delta_eb"] = d_eb - mu_d
    m_w, v_w, _ = _cluster_mean(gp, "S_wpa", k, P)
    out["raw_press_wpa100"] = 100 * m_w
    imp, mu_i, tau_i = _eb(100 * m_w, 1e4 * v_w, pool)
    prior["impact"] = float(np.sqrt(tau_i))
    out["impact"] = imp
    out["press_weight"] = N_p

    g = prep.inn
    ki = k[g["match"]] * g["w"]
    Nn = np.bincount(g["player"], ki, minlength=P)
    H = np.bincount(g["player"], ki * g["hit"], minlength=P)
    B = np.bincount(g["player"], ki * g["bad"], minlength=P)
    pool_i = prep.n_press_inn >= 5
    hit, m_h, ab_h = _beta_shrink(H, Nn, pool_i)
    bad, m_b, ab_b = _beta_shrink(B, Nn, pool_i)
    prior["consistency"] = float(np.sqrt(_beta_sd(m_h, ab_h) ** 2 + _beta_sd(m_b, ab_b) ** 2))
    out["hit_rate"] = hit
    out["downside"] = bad
    out["consistency"] = hit - bad
    out["raw_hit_rate"] = np.where(Nn > 0, H / np.maximum(Nn, 1e-12), np.nan)
    out["raw_downside"] = np.where(Nn > 0, B / np.maximum(Nn, 1e-12), np.nan)
    out.attrs["prior_sd"] = prior
    return out


def composite(tab, eligible, weights=None, estimator="ridge", standardise=None):
    """Standardise the four components among eligible players and combine. Returns a copy of the
    eligible rows with z columns, rating and rank.

    standardise='zscore'   (pre-registered) centre and divide by the SD of the shrunk values among
                           eligible players. Every component then has unit spread whatever its signal.
    standardise='prior_sd' centre and divide by the estimated between-player SD of the true quantity
                           (the prior SD of the shrinkage model). A component the data cannot separate
                           players on then has a small spread and moves the rating little.
    """
    cw = weights or CFG["composite_weights"]
    standardise = standardise or CFG.get("composite", {}).get("standardise", "zscore")
    prior = tab.attrs.get("prior_sd", {})
    t = tab[eligible].copy()
    src = {"level": "level", "impact": "impact", "consistency": "consistency", "delta": "delta"}
    if estimator == "eb":
        src["level"], src["delta"] = "level_eb", "delta_eb"
    rating = np.zeros(len(t))
    for c in COMPONENTS:
        x = t[src[c]].values.astype(float)
        sd = np.nanstd(x) if standardise == "zscore" else float(prior.get(src[c], 0.0))
        z = (x - np.nanmean(x)) / sd if sd > 1e-12 else np.zeros(len(t))
        t[f"z_{c}"] = z
        rating += cw[c] * z
    t["rating"] = rating
    t["rank"] = t.rating.rank(ascending=False, method="first").astype(int)
    return t.sort_values("rank")


def z_matrix(tab, eligible, estimator="ridge"):
    """n_eligible x 4 matrix of component z-scores (for fast weight perturbation)."""
    t = composite(tab, eligible, estimator=estimator)
    return t.player_id.values, t[[f"z_{c}" for c in COMPONENTS]].values


# ---- descriptive statistics (plain cricket numbers shown next to the model outputs) -------------------
def describe(df, role, pcol="pA"):
    d = df.copy()
    d["press"] = d[pcol].astype(bool)
    d["weak_opp"] = (d.tier == "A-team") | ((d.tier == "T20I") & d.opp_assoc)
    rows = []
    for pid, g in d.groupby("player_id", sort=True):
        r = dict(player_id=pid)
        for lab, s in [("press", g[g.press]), ("normal", g[~g.press])]:
            if role == "bat":
                f = s[s.faced == 1]
                n = len(f)
                r[f"{lab}_balls"] = n
                r[f"{lab}_runs"] = int(f.runs.sum())
                r[f"{lab}_sr"] = 100 * f.runs.sum() / n if n else np.nan
                r[f"{lab}_outs"] = int(s.out.sum())
                r[f"{lab}_avg"] = f.runs.sum() / s.out.sum() if s.out.sum() else np.nan
                r[f"{lab}_boundary_pct"] = 100 * (f.is_four | f.is_six).mean() if n else np.nan
                r[f"{lab}_dot_pct"] = 100 * (f.runs == 0).mean() if n else np.nan
            else:
                n = len(s)
                r[f"{lab}_balls"] = n
                r[f"{lab}_runs"] = float(s.bowler_runs.sum())
                r[f"{lab}_econ"] = 6 * s.bowler_runs.sum() / n if n else np.nan
                r[f"{lab}_wkts"] = int(s.wkt.sum())
                r[f"{lab}_sr"] = n / s.wkt.sum() if s.wkt.sum() else np.nan
                r[f"{lab}_dot_pct"] = 100 * (s.bowler_runs == 0).mean() if n else np.nan
        p = g[g.press]
        r["press_innings"] = p[["match_id", "innings"]].drop_duplicates().shape[0]
        r["press_wpa_total"] = p.wpa.sum()
        r["press_share_weak_opp"] = p.weak_opp.mean() if len(p) else np.nan
        r["press_share_ipl"] = (p.tier == "IPL").mean() if len(p) else np.nan
        r["press_share_death"] = (p.phase == "death").mean() if len(p) else np.nan
        r["press_share_innings2"] = (p.innings == 2).mean() if len(p) else np.nan
        per = p.groupby(["match_id", "innings"]).nrae.sum()
        r["press_innings_nrae_median"] = per.median() if len(per) else np.nan
        r["press_innings_nrae_mad"] = (per - per.median()).abs().median() if len(per) else np.nan
        r["matches"] = g.match_id.nunique()
        r["first_year"] = int(g.year.min()); r["last_year"] = int(g.year.max())
        rows.append(r)
    return pd.DataFrame(rows)


def latest_teams(df, mapping, teams_ipl):
    """Most recent IPL franchise (by season) and national side for each player, from the mapping file."""
    mp = mapping.copy()
    mp["is_ipl"] = mp.comp_name.str.startswith("IPL")
    mp["season"] = mp.comp_name.str.extract(r"(20\d\d)").astype(float)
    ipl = mp[mp.is_ipl].sort_values("season").groupby("player_id").tail(1).set_index("player_id")
    ipl26 = mp[mp.comp_name == "IPL 2026"].drop_duplicates("player_id").set_index("player_id").team_name
    nat = mp[~mp.is_ipl & ~mp.team_name.str.endswith(" A")]
    nat = nat.groupby("player_id").team_name.agg(lambda s: s.value_counts().index[0])
    return ipl.team_name, ipl.season, ipl26, nat
