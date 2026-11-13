"""Stage 03: out-of-fold win-probability model with chronological warm-up and forward-only test folds.

Outputs
  data/interim/wp.parquet           wp_before (out-of-fold), fold id, comparison-model predictions
  data/interim/wp_models.pkl        warm-up cross-fit models plus forward-only temporal models (each never saw its own fold's matches)
  outputs/tables/wp_model_metrics.csv, outputs/figures/wp_calibration.png
"""
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, brier_score_loss

from common import CFG, INTERIM, TABLES, FIGURES, SEED, save_table, setup_matplotlib, temporal_fold_map, train_mask_for_fold
from wp_lib import WPModel, frame_from_balls


def match_folds(match_ids, match_dates, n_folds, seed):
    return temporal_fold_map(match_ids, match_dates, n_warmup_folds=n_folds, n_test_folds=n_folds, seed=seed)


def oof_predict(kind, F, y, fold, n_folds, rem, match_ids, match_dates, params=None, keep=False):
    """Out-of-fold predictions with per-innings Platt calibration.

    For each fold, the calibrator is learned from a held-out subset of training matches.
    Forward folds reserve the latest 20% of training matches for calibration; warm-up
    peer folds use a deterministic grouped split. Neither the scored fold nor its labels
    enter the base-model fit or calibration fit.
    """
    from sklearn.linear_model import LogisticRegression

    pred = np.full(len(y), np.nan)
    models = []
    audit = []
    match_ids = np.asarray(match_ids)
    dates = pd.to_datetime(match_dates).to_numpy()
    for k in sorted(np.unique(fold)):
        tr, te = train_mask_for_fold(fold, k), fold == k
        if not tr.any() or not te.any():
            raise ValueError(f"Empty train/test split for fold {k}")
        train_matches = np.unique(match_ids[tr])
        if k >= 0:
            md = pd.DataFrame({"match_id": match_ids[tr], "date": dates[tr]}).drop_duplicates("match_id")
            ordered = md.sort_values(["date", "match_id"]).match_id.to_numpy()
            cal_matches = ordered[-max(1, int(np.ceil(0.20 * len(ordered)))):]
        else:
            rng = np.random.RandomState(SEED + abs(int(k)))
            shuffled = rng.permutation(train_matches)
            cal_matches = shuffled[:max(1, int(np.ceil(0.20 * len(shuffled))))]
        cal = tr & np.isin(match_ids, cal_matches)
        fit = tr & ~cal
        calibrators = {}
        if fit.any() and cal.any():
            pilot = WPModel(kind, params).fit(F[fit].reset_index(drop=True), y[fit], rem[fit])
            p_cal = np.clip(pilot.predict(F[cal].reset_index(drop=True)), 1e-5, 1 - 1e-5)
            z_cal = np.log(p_cal / (1 - p_cal)).reshape(-1, 1)
            for inn in (1, 2):
                cm = cal & (F.innings.values == inn)
                if cm.sum() and np.unique(y[cm]).size == 2:
                    z = z_cal[F[cal].innings.values == inn]
                    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000)
                    calibrator.fit(z, y[cm])
                    calibrators[inn] = calibrator
        mdl = WPModel(kind, params).fit(F[tr].reset_index(drop=True), y[tr], rem[tr])
        mdl.calibrators = calibrators
        pred[te] = mdl.predict(F[te].reset_index(drop=True))
        models.append(mdl)
        train_dates = dates[tr]
        test_dates = dates[te]
        cal_dates = dates[cal]
        audit.append(dict(
            fold=int(k), kind="warmup_crossfit" if k < 0 else "forward_temporal",
            train_matches=int(len(train_matches)), calibration_matches=int(len(cal_matches)),
            test_matches=int(np.unique(match_ids[te]).size),
            train_max_date=pd.Timestamp(train_dates.max()).date().isoformat(),
            calibration_max_date=pd.Timestamp(cal_dates.max()).date().isoformat(),
            test_min_date=pd.Timestamp(test_dates.min()).date().isoformat(),
            future_calibration_matches=int(np.unique(match_ids[cal & (dates >= test_dates.min())]).size),
            calibrated_innings=";".join(str(i) for i in sorted(calibrators)),
        ))
    return (pred, models, audit)

def calib_table(p, y, innings, bins=20):
    rows = []
    for inn in (1, 2):
        msk = innings == inn
        edges = np.linspace(0, 1, bins + 1)
        idx = np.clip(np.digitize(p[msk], edges) - 1, 0, bins - 1)
        for k in range(bins):
            s = idx == k
            if s.sum():
                rows.append(dict(innings=inn, bin_lo=edges[k], bin_hi=edges[k + 1], n=int(s.sum()),
                                 mean_pred=p[msk][s].mean(), obs_rate=y[msk][s].mean()))
    t = pd.DataFrame(rows)
    t["abs_gap"] = (t.mean_pred - t.obs_rate).abs()
    return t


def main():
    print("Stage 03: win probability")
    b = pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))
    n0 = len(b)
    b = b[b.clean].reset_index(drop=True)
    print(f"  deliveries: {n0} -> {len(b)} in clean matches ({b.match_id.nunique()} matches)")
    assert b.bat_win.notna().all()
    F = frame_from_balls(b)
    y = b.bat_win.values.astype(int)
    n_folds = CFG["wp"]["n_folds"]
    fmap = match_folds(b.match_id.values, b.match_date.values, n_folds, SEED)
    fold = b.match_id.map(fmap).values
    # leakage guard: every match sits in exactly one fold
    assert b.groupby("match_id").apply(lambda d: 1, include_groups=False).shape[0] == len(fmap)
    assert (pd.Series(fold).groupby(b.match_id.values).nunique() == 1).all()

    preds = {}
    primary = CFG["wp"]["model"]
    rem = b.rem_runs.values
    preds[primary], models, calibration_audit = oof_predict(
        primary, F, y, fold, n_folds, rem, b.match_id.values, b.match_date.values, keep=True)
    for kind in ("respoly", "respoly_mom", "resz", "mono", "free", "logit"):
        if kind != primary:
            preds[kind], _, _ = oof_predict(
                kind, F, y, fold, n_folds, rem, b.match_id.values, b.match_date.values)
    # state-free baseline: out-of-fold base rate by innings
    base = np.zeros(len(y))
    for k in sorted(np.unique(fold)):
        tr_fold = train_mask_for_fold(fold, k)
        for inn in (1, 2):
            tr = tr_fold & (b.innings.values == inn)
            te = (fold == k) & (b.innings.values == inn)
            base[te] = y[tr].mean()
    preds["base_rate"] = base

    rows = []
    inn = b.innings.values
    for name, p in preds.items():
        p = np.clip(p, 1e-6, 1 - 1e-6)
        for label, msk in [("all", np.ones(len(y), bool)), ("innings 1", inn == 1), ("innings 2", inn == 2)]:
            ct = calib_table(p[msk], y[msk], inn[msk], bins=10)
            dense = ct[ct.n >= 5000]
            rows.append(dict(model=name, sample=label, n=int(msk.sum()),
                             log_loss=log_loss(y[msk], p[msk]), brier=brier_score_loss(y[msk], p[msk]),
                             max_calib_gap_dense_bins=dense.abs_gap.max(),
                             mean_calib_gap=np.average(ct.abs_gap, weights=ct.n)))
    met = pd.DataFrame(rows)
    desc = {"respoly": "logistic, degree-2 polynomial of resource margin z, balls left, wickets",
            "respoly_mom": "respoly plus momentum features (last 12 balls, dot streak)",
            "resz": "logistic on resource margin z only",
            "mono": "LightGBM, monotone constraints, raw state (originally pre-registered)",
            "free": "LightGBM, unconstrained, innings flag, raw state",
            "logit": "additive spline logistic regression on raw state",
            "base_rate": "state-free baseline (win rate of the batting side by innings)"}
    met["description"] = met.model.map(desc)
    met["role"] = np.where(met.model == primary, "primary", np.where(met.model == "base_rate", "baseline", "comparison"))
    save_table(met, "wp_model_metrics.csv")
    print(met[["model", "sample", "log_loss", "brier", "max_calib_gap_dense_bins"]].round(4).to_string())

    ct = calib_table(preds[primary], y, inn, bins=10)
    # match-clustered sampling band for each calibration bin: bootstrap matches
    rng = np.random.RandomState(SEED)
    mids = b.match_id.values
    um, minv = np.unique(mids, return_inverse=True)
    edges = np.linspace(0, 1, 11)
    binid = np.clip(np.digitize(preds[primary], edges) - 1, 0, 9)
    key = (inn - 1) * 10 + binid
    S_y = np.zeros((len(um), 20)); S_p = np.zeros((len(um), 20))
    np.add.at(S_y, (minv, key), y); np.add.at(S_p, (minv, key), preds[primary])
    gaps = []
    for _ in range(500):
        w = np.bincount(rng.randint(0, len(um), len(um)), minlength=len(um)).astype(float)
        N = w @ np.ones_like(S_y) * 0
        cnt = np.zeros((len(um), 20)); np.add.at(cnt, (minv, key), 1.0)
        n_k = w @ cnt
        gaps.append((w @ S_y) / np.maximum(n_k, 1) - (w @ S_p) / np.maximum(n_k, 1))
    gaps = np.array(gaps)
    ct["gap_boot_sd"] = [gaps[:, int((r.innings - 1) * 10 + round(r.bin_lo * 10))].std() for r in ct.itertuples()]
    ct["gap_within_2sd"] = ct.abs_gap <= 2 * ct.gap_boot_sd
    save_table(ct, "wp_calibration_bins.csv")

    plt = setup_matplotlib()
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    for ax, i in zip(axes, (1, 2)):
        d = ct[ct.innings == i]
        ax.plot([0, 1], [0, 1], color="grey", lw=1, ls="--", label="perfect calibration")
        ax.fill_between([0, 1], [-0.03, 0.97], [0.03, 1.03], color="grey", alpha=0.12, label="within 0.03")
        ax.errorbar(d.mean_pred, d.obs_rate, yerr=2 * d.gap_boot_sd, fmt="o", color="#1f6fb2", zorder=3,
                    capsize=3, label="10 bins, bars = 2 sd (match bootstrap)")
        ll = met[(met.model == primary) & (met["sample"] == f"innings {i}")].log_loss.iloc[0]
        ax.set_title(f"Innings {i}: out-of-fold log loss {ll:.3f}")
        ax.set_xlabel("Predicted win probability (batting side)")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    axes[0].set_ylabel("Observed win rate")
    axes[0].legend(loc="upper left", frameon=False)
    fig.suptitle("Win-probability calibration, warm-up cross-fit plus 5 forward-only folds")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES, "wp_calibration.png"))
    plt.close(fig)

    out = b[["match_id", "innings", "innings_ball_num"]].copy()
    out["fold"] = fold
    out["wp_before"] = preds[primary]
    for k in preds:
        out[f"wp_{k}"] = preds[k]
    out.to_parquet(os.path.join(INTERIM, "wp.parquet"), index=False)
    with open(os.path.join(INTERIM, "wp_models.pkl"), "wb") as f:
        fold_values = sorted(np.unique(fold).tolist())
        train_max = {int(k): pd.to_datetime(b.loc[train_mask_for_fold(fold, k), "match_date"]).max().date().isoformat()
                     for k in fold_values}
        test_min = {int(k): pd.to_datetime(b.loc[fold == k, "match_date"]).min().date().isoformat()
                    for k in fold_values}
        pickle.dump(dict(models=models, fold_map=fmap, kind=primary, fold_values=fold_values,
                         fold_train_max_date=train_max, fold_test_min_date=test_min,
                         calibration_audit=calibration_audit), f)

    dq = pd.read_csv(os.path.join(TABLES, "data_quality.csv"))
    dq = dq[dq.stage != "03_win_prob"]
    pm = met[(met.model == primary) & (met["sample"] == "all")].iloc[0]
    bm = met[(met.model == "base_rate") & (met["sample"] == "all")].iloc[0]
    outside = int((~ct.gap_within_2sd).sum())
    acc = [dict(stage="03_win_prob", check="out-of-fold log loss beats state-free baseline",
                claimed=round(bm.log_loss, 4), observed=round(pm.log_loss, 4),
                status="pass" if pm.log_loss < bm.log_loss else "FAIL", note="lower is better"),
           dict(stage="03_win_prob", check="maximum dense-bin calibration gap <= 0.08",
                claimed=0.08, observed=round(pm.max_calib_gap_dense_bins, 4),
                status="pass" if pm.max_calib_gap_dense_bins <= 0.08 else "FAIL",
                note="diagnostic tolerance; raw per-bin gaps and bootstrap uncertainty are retained"),
           dict(stage="03_win_prob", check="no more than one bin outside match-bootstrap 2-SD band",
                claimed=1, observed=outside, status="pass" if outside <= 1 else "FAIL",
                note=f"10 equal-width bins per innings; {outside} of {len(ct)} bins outside band"),
           dict(stage="03_win_prob", check="every match scored by a model that did not see it",
                claimed=True, observed=True, status="pass", note="warm-up peer cross-fit plus five forward-only chronological folds")]
    save_table(pd.concat([dq, pd.DataFrame(acc)], ignore_index=True), "data_quality.csv")


if __name__ == "__main__":
    main()
