"""Run-resource table: expected runs still to come in a first innings with b balls left and
w wickets lost, R_w(b) = a_w * (1 - exp(-b / t_w)). Smooth, monotone in b by construction."""
import numpy as np
import pandas as pd
from scipy.optimize import least_squares


def fit_resource(balls_left, wickets, remaining_runs):
    d = pd.DataFrame({"b": np.asarray(balls_left, dtype=float), "w": np.asarray(wickets, dtype=int),
                      "r": np.asarray(remaining_runs, dtype=float)})
    d = d[(d.w >= 0) & (d.w <= 9) & (d.b > 0)]
    c = d.groupby(["w", "b"]).r.agg(["mean", "count"]).reset_index()
    wv, bv, mv, sw = c.w.values, c.b.values, c["mean"].values, np.sqrt(c["count"].values)

    gb = np.arange(1.0, 121.0, 3.0)

    def resid(p):
        fit = (p[:10][wv] * (1 - np.exp(-bv / p[10:][wv])) - mv) * sw
        # non-crossing penalty: with the same balls left, one more wicket down never means more runs
        curves = p[:10, None] * (1 - np.exp(-gb[None, :] / p[10:, None]))
        cross = np.maximum(curves[1:] - curves[:-1], 0.0).ravel() * 30.0
        return np.r_[fit, cross]

    p0 = np.r_[np.linspace(280, 40, 10), np.linspace(180, 40, 10)]
    lo = np.r_[np.full(10, 5.0), np.full(10, 5.0)]
    hi = np.r_[np.full(10, 600.0), np.full(10, 2000.0)]
    return least_squares(resid, p0, bounds=(lo, hi)).x


def resource(p, balls_left, wickets):
    w = np.clip(np.asarray(wickets).astype(int), 0, 10)
    a = np.r_[p[:10], 0.0][w]
    t = np.r_[p[10:], 1.0][w]
    return a * (1 - np.exp(-np.maximum(np.asarray(balls_left, dtype=float), 0.0) / t))


def wicket_value(p, balls_left, wickets):
    """Run cost of losing a wicket on a ball bowled with balls_left remaining before it:
    drop in expected remaining runs after the ball, from w to w+1 wickets down. Never negative."""
    b_after = np.asarray(balls_left, dtype=float) - 1.0
    return np.maximum(resource(p, b_after, wickets) - resource(p, b_after, np.asarray(wickets) + 1), 0.0)
