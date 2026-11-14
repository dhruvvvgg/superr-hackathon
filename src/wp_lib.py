"""Win-probability helpers shared by stages 03 and 04 (feature construction, fold models,
terminal-state handling)."""
import numpy as np
import pandas as pd
import lightgbm as lgb

from common import SEED
from res_lib import fit_resource, resource

TIER_CODE = {"IPL": 0, "T20I": 1, "A-team": 2}

# feature name -> monotone direction (for the batting side's win probability)
FEATS_MONO = {
    1: {"balls_left": 1, "score": 1, "wickets": -1, "venue_avg": -1, "runs_last12": 0,
        "wkts_last12": 0, "dot_streak": 0, "tier": 0},
    2: {"balls_left": 1, "runs_needed": -1, "wickets": -1, "rrr": -1, "target": 0, "venue_avg": 0,
        "runs_last12": 0, "wkts_last12": 0, "dot_streak": 0, "tier": 0},
}
FEATS_FREE = ["innings", "balls_left", "score", "wickets", "crr", "runs_needed", "rrr", "rrr_gap",
              "target", "venue_avg", "runs_last12", "wkts_last12", "dot_streak", "tier"]

def state_frame(innings, legal_before, score, wickets, target, runs_last12, wkts_last12,
                dot_streak, venue_avg, tier_code):
    """Build the full feature frame from raw state arrays."""
    innings = np.asarray(innings)
    legal_before = np.asarray(legal_before, dtype=float)
    score = np.asarray(score, dtype=float)
    balls_left = 120.0 - legal_before
    f = pd.DataFrame({"innings": innings, "balls_left": balls_left, "score": score,
                      "wickets": np.asarray(wickets, dtype=float)})
    f["crr"] = np.where(legal_before > 0, score / np.maximum(legal_before / 6.0, 1e-9), np.nan)
    tgt = np.where(innings == 2, np.asarray(target, dtype=float), np.nan)
    f["target"] = tgt
    f["runs_needed"] = tgt - score
    f["rrr"] = np.clip(f.runs_needed / np.maximum(balls_left, 0.5) * 6.0, 0, 40)
    f.loc[innings != 2, "rrr"] = np.nan
    f["rrr_gap"] = f.rrr - f.crr.fillna(f.rrr)
    f["venue_avg"] = np.asarray(venue_avg, dtype=float)
    f["runs_last12"] = np.asarray(runs_last12, dtype=float)
    f["wkts_last12"] = np.asarray(wkts_last12, dtype=float)
    f["dot_streak"] = np.asarray(dot_streak, dtype=float)
    f["tier"] = np.asarray(tier_code, dtype=float)
    return f


def frame_from_balls(b):
    return state_frame(b.innings.values, b.legal_before.values, b.score_before.values,
                       b.wkts_before.values, b.target.values, b.runs_last12.values,
                       b.wkts_last12.values, b.dot_streak.values, b.venue_avg.values,
                       b.tier.map(TIER_CODE).values)


LGB_PARAMS = dict(objective="binary", learning_rate=0.03, n_estimators=150, num_leaves=15,
                  min_child_samples=400, subsample=0.8, subsample_freq=1, colsample_bytree=0.9,
                  reg_lambda=5.0, random_state=SEED, n_jobs=4, deterministic=True,
                  force_row_wise=True, verbose=-1)

RES_COLS = {"respoly": ["z", "bl", "wk"],
            "respoly_mom": ["z", "bl", "wk", "runs_last12", "wkts_last12", "dot_streak"],
            "resz": ["z"]}


class WPModel:
    """Win-probability model for the batting side, one sub-model per innings.

    kind
      'respoly'      primary: logistic regression on a degree-2 polynomial of (z, balls left,
                     wickets lost), where z is the resource-adjusted margin: in a chase,
                     (expected remaining runs - runs needed) / sqrt(balls left + 3); in the first
                     innings, (projected total - venue average) / sqrt(balls left + 20).
                     The resource table is fitted on the training folds only.
      'respoly_mom'  the same plus momentum features
      'resz'         z only
      'mono'         LightGBM with monotone constraints on the raw state (pre-registered model)
      'free'         single unconstrained LightGBM with an innings flag
      'logit'        additive spline logistic regression on the raw state
    """

    def __init__(self, kind="respoly", params=None):
        self.kind = kind
        self.params = dict(LGB_PARAMS, **(params or {}))
        self.models = {}
        self.res = None
        self.vmean = None
        self.calibrators = {}

    # -- resource features -----------------------------------------------------------------
    def _res_feats(self, F, inn):
        vf = F.venue_avg.values / self.vmean
        r = resource(self.res, F.balls_left.values, F.wickets.values) * vf
        bl = F.balls_left.values
        if inn == 2:
            z = (r - F.runs_needed.values) / np.sqrt(bl + 3.0)
        else:
            z = (F.score.values + r - F.venue_avg.values) / np.sqrt(bl + 20.0)
        out = pd.DataFrame({"z": z, "bl": bl, "wk": F.wickets.values})
        for c in ("runs_last12", "wkts_last12", "dot_streak"):
            out[c] = F[c].values
        return out

    def fit(self, F, y, rem_runs=None):
        if self.kind in RES_COLS:
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import PolynomialFeatures, StandardScaler
            i1 = (F.innings == 1).values
            self.res = fit_resource(F.balls_left.values[i1], F.wickets.values[i1], np.asarray(rem_runs)[i1])
            self.vmean = float(F.venue_avg.values[i1].mean())
            for inn in (1, 2):
                msk = (F.innings == inn).values
                X = self._res_feats(F[msk], inn)[RES_COLS[self.kind]]
                mdl = make_pipeline(StandardScaler(), PolynomialFeatures(2, include_bias=False),
                                    StandardScaler(), LogisticRegression(C=0.01, max_iter=5000))
                self.models[inn] = (mdl.fit(X.values, y[msk]), RES_COLS[self.kind])
            return self
        if self.kind == "free":
            self.models[0] = lgb.LGBMClassifier(**self.params).fit(F[FEATS_FREE], y)
            return self
        spec = FEATS_MONO
        for inn in (1, 2):
            msk = (F.innings == inn).values
            cols = list(spec[inn])
            if self.kind == "logit":
                from sklearn.linear_model import LogisticRegression
                from sklearn.pipeline import make_pipeline
                from sklearn.preprocessing import StandardScaler, SplineTransformer
                mdl = make_pipeline(SplineTransformer(n_knots=6, degree=3), StandardScaler(),
                                    LogisticRegression(C=0.003, max_iter=3000))
                mdl.fit(F.loc[msk, cols].fillna(0.0), y[msk])
            else:
                mdl = lgb.LGBMClassifier(monotone_constraints=[spec[inn][c] for c in cols],
                                         monotone_constraints_method="advanced", **self.params)
                mdl.fit(F.loc[msk, cols], y[msk])
            self.models[inn] = (mdl, cols)
        return self

    def _apply_calibration(self, probabilities, innings):
        """Apply fold-local Platt calibration, separately by innings."""
        out = np.asarray(probabilities, dtype=float).copy()
        innings = np.asarray(innings)
        for inn, calibrator in self.calibrators.items():
            mask = innings == inn
            if mask.any():
                p = np.clip(out[mask], 1e-5, 1 - 1e-5)
                out[mask] = calibrator.predict(p)
        return np.clip(out, 1e-6, 1 - 1e-6)

    def predict(self, F):
        out = np.full(len(F), np.nan)
        if self.kind == "free":
            out = self.models[0].predict_proba(F[FEATS_FREE])[:, 1]
            return self._apply_calibration(out, F.innings.values)
        for inn in (1, 2):
            msk = (F.innings == inn).values
            if msk.any():
                mdl, cols = self.models[inn]
                if self.kind in RES_COLS:
                    X = self._res_feats(F[msk], inn)[cols].values
                else:
                    X = F.loc[msk, cols]
                    if self.kind == "logit":
                        X = X.fillna(0.0)
                out[msk] = mdl.predict_proba(X)[:, 1]
        return self._apply_calibration(out, F.innings.values)


def wp_states(model, innings, legal_before, score, wickets, target, r12, w12, dot, venue, tier):
    """Win probability of the batting side for arbitrary (possibly terminal) states.
    Terminal rules: chase complete -> 1; chase out of balls or wickets -> 0 (0.5 if scores level);
    first innings finished -> 1 - WP of the chasing side at the start of the chase."""
    innings = np.asarray(innings)
    legal_before = np.asarray(legal_before, dtype=float)
    score = np.asarray(score, dtype=float)
    wickets = np.asarray(wickets, dtype=float)
    target = np.asarray(target, dtype=float)
    n = len(innings)
    out = np.full(n, np.nan)
    done = (legal_before >= 120) | (wickets >= 10)
    i2 = innings == 2
    need = np.where(i2, target - score, np.nan)
    won = i2 & (need <= 1e-9)
    out[won] = 1.0
    lost = i2 & done & ~won
    out[lost] = np.where(need[lost] <= 1.0 + 1e-9, 0.5, 0.0)
    end1 = (~i2) & done
    live = ~(won | lost | end1)
    venue = np.asarray(venue, dtype=float)
    tier = np.asarray(tier, dtype=float)
    if live.any():
        F = state_frame(innings[live], legal_before[live], score[live], wickets[live], target[live],
                        np.asarray(r12)[live], np.asarray(w12)[live], np.asarray(dot)[live],
                        venue[live], tier[live])
        out[live] = model.predict(F)
    if end1.any():
        k = int(end1.sum())
        F = state_frame(np.full(k, 2), np.zeros(k), np.zeros(k), np.zeros(k), score[end1] + 1.0,
                        np.zeros(k), np.zeros(k), np.zeros(k), venue[end1], tier[end1])
        out[end1] = 1.0 - model.predict(F)
    return out
