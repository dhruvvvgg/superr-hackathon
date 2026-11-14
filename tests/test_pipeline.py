"""Acceptance checks from section 11 of the handover plus leakage and silent-error guards.
Run after `python run_all.py`."""
import os
import pickle
import re
import subprocess

import numpy as np
import pandas as pd
import pytest

from common import CFG, ROOT, INTERIM, PROCESSED, TABLES, raw, parse_result

T = lambda n: pd.read_csv(os.path.join(TABLES, n))


@pytest.fixture(scope="module")
def balls():
    return pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))


@pytest.fixture(scope="module")
def minfo():
    return pd.read_parquet(os.path.join(INTERIM, "match_info.parquet"))


@pytest.fixture(scope="module")
def bat():
    return pd.read_parquet(os.path.join(PROCESSED, "bat_credit.parquet"))


@pytest.fixture(scope="module")
def bowl():
    return pd.read_parquet(os.path.join(PROCESSED, "bowl_credit.parquet"))


# ---- legal balls ---------------------------------------------------------------------------------
def test_no_innings_exceeds_120_legal_balls(balls):
    assert balls.groupby(["match_id", "innings"]).legal.sum().max() <= 120


def test_six_legal_balls_in_nearly_every_full_over(balls):
    last = balls.groupby(["match_id", "innings"]).overid.transform("max")
    oc = balls[balls.overid < last].groupby(["match_id", "innings", "overid"]).legal.sum()
    assert (oc == 6).mean() >= 0.999
    assert (oc > 6).sum() <= 1


def test_complete_innings_have_120_legal_balls(balls, minfo):
    clean = minfo[minfo.clean]
    assert ((clean.lb_1 == 120) | (clean.wk_1 >= 10)).all()


def test_no_super_overs_or_reduced_matches_downstream(balls, minfo, bat, bowl):
    assert set(balls.innings.unique()) <= {1, 2}
    bad = set(minfo[minfo.reduced | ~minfo.clean].match_id)
    for t in (bat, bowl):
        assert not (set(t.match_id) & bad)
        assert set(t.innings.unique()) <= {1, 2}


# ---- wickets and extras ----------------------------------------------------------------------------
def test_wicket_check_against_results(minfo):
    wk = minfo[minfo.has_balls & (minfo.res_kind == "wkts")]
    ok = (10 - wk.res_n) == wk.wk_2
    assert ok.all()                          # match 20190's result string is corrected by config (D-24)


def test_source_overrides_are_only_the_documented_one():
    assert set(CFG["source_overrides"]["result_fixes"]) == {"20190"}
    raw_m = raw("matches").set_index("match_id")
    assert raw_m.loc[20190, "result"] == CFG["source_overrides"]["result_fixes"]["20190"]["raw_result"]


def test_extras_calibration_is_strictly_past_only():
    detail = T("extras_calibration_by_match.csv")
    assert detail.match_id.is_unique
    assert detail.calibration_method.isin(["one_run_fallback", "expanding_lad"]).all()
    trained = detail[detail.calibration_method == "expanding_lad"]
    assert len(trained) > 0
    assert (trained.calibration_training_matches >= 40).all()
    assert (pd.to_datetime(trained.calibration_max_training_date) <
            pd.to_datetime(trained.match_date)).all()
    metrics = T("extras_calibration.csv").set_index("item")
    assert np.isfinite(metrics.loc["margin MAE (runs), fitted", "fitted"])
    assert np.isfinite(metrics.loc["margin MAE (runs), simple", "fitted"])


def test_chase_target_uses_only_first_innings_reconstruction(minfo):
    clean = minfo[minfo.clean]
    expected = np.rint(clean.tot_1.to_numpy(dtype=float)) + 1.0
    assert np.allclose(clean.target.to_numpy(dtype=float), expected)
    assert np.allclose(clean.target_recon.to_numpy(dtype=float), expected)
    assert clean.target_source.eq("first_innings_ball_reconstruction").all()
    assert "target_anchored" not in clean.columns


# ---- win probability ---------------------------------------------------------------------------------
def test_wp_beats_state_free_baseline():
    m = T("wp_model_metrics.csv")
    p = m[(m.role == "primary") & (m["sample"] == "all")].log_loss.iloc[0]
    b = m[(m.role == "baseline") & (m["sample"] == "all")].log_loss.iloc[0]
    assert p < b - 0.1


def test_wp_calibration_is_within_diagnostic_tolerance():
    m = T("wp_model_metrics.csv")
    primary = m[(m.role == "primary") & (m["sample"] == "all")].iloc[0]
    bins = T("wp_calibration_bins.csv")
    assert primary.max_calib_gap_dense_bins <= 0.08
    broad = bins[bins.n >= 2500]
    assert broad.abs_gap.max() <= 0.12
    assert int((~bins.gap_within_2sd).sum()) <= 1
    assert int((~broad.gap_within_2sd).sum()) <= 3
    quality = T("data_quality.csv")
    gate = quality[quality.check.isin([
        "maximum dense-bin calibration gap <= 0.08",
        "no more than one bin outside match-bootstrap 2-SD band",
        "calibration gap <= 0.12 in bins with at least 2500 balls",
        "no more than three bins with at least 2500 balls outside match-bootstrap 2-SD band"
    ])]
    assert len(gate) == 2 and gate.status.eq("pass").all()


def test_no_match_scored_by_a_model_that_saw_it():
    wp = pd.read_parquet(os.path.join(INTERIM, "wp.parquet"))
    assert (wp.groupby("match_id").fold.nunique() == 1).all()
    with open(os.path.join(INTERIM, "wp_models.pkl"), "rb") as f:
        pk = pickle.load(f)
    fm = pd.Series(pk["fold_map"])
    assert (wp.drop_duplicates("match_id").set_index("match_id").fold == fm.reindex(wp.match_id.unique())).all()
    assert wp.wp_before.between(0, 1).all()
    assert set(pk["fold_values"]) == set(range(-CFG["wp"]["n_folds"], CFG["wp"]["n_folds"]))
    for k in pk["fold_values"]:
        if k >= 0:
            assert pk["fold_train_max_date"][k] < pk["fold_test_min_date"][k]
    audit = pd.DataFrame(pk["calibration_audit"])
    assert len(audit) == len(pk["fold_values"])
    assert (audit.calibration_matches <= audit.train_matches).all()
    assert (audit.model_fit_matches + audit.calibration_matches == audit.train_matches).all()
    assert (audit.calibration_matches_outside_train == 0).all()
    assert (audit.calibration_matches_in_test == 0).all()
    forward_audit = audit[audit.fold >= 0]
    assert (forward_audit.future_calibration_matches == 0).all()
    assert (pd.to_datetime(forward_audit.model_fit_max_date) <
            pd.to_datetime(forward_audit.calibration_max_date)).all()
    assert (pd.to_datetime(forward_audit.calibration_max_date) <
            pd.to_datetime(forward_audit.test_min_date)).all()
    assert audit.calibrated_innings.eq("1;2").all()
    assert audit.calibration_method.eq("match_weighted_platt").all()
    exported = T("wp_calibration_fold_audit.csv")
    assert len(exported) == len(audit)
    assert (exported.calibration_matches_in_test == 0).all()


def test_wpa_sums_to_result(balls):
    """Per match, win-probability changes telescope: the side batting second ends at its result."""
    pr = pd.read_parquet(os.path.join(INTERIM, "pressure.parquet"))
    d = pr.merge(balls[["match_id", "innings", "innings_ball_num", "bat_win"]], on=["match_id", "innings", "innings_ball_num"])
    i2 = d[d.innings == 2]
    g = i2.groupby("match_id")
    assert np.allclose(g.wp_before.first() + g.wpa.sum(), g.bat_win.first(), atol=1e-9)


# ---- attribution guards --------------------------------------------------------------------------------
def test_wides_are_not_balls_faced(balls, bat):
    clean = balls[balls.clean]
    assert int(bat.faced.sum()) == int((~clean.is_wide).sum())
    key = ["match_id", "innings", "innings_ball_num"]
    wides = clean[clean.is_wide][key]
    faced = bat[bat.faced == 1][key]
    assert len(faced.merge(wides, on=key)) == 0


def test_run_outs_not_credited_to_bowlers(balls, bowl):
    clean = balls[balls.clean]
    credited = clean[clean.is_wicket & clean.dismissal_type.isin(CFG["bowler_wickets"])]
    assert int(bowl.wkt.sum()) == len(credited)
    assert "RunOut" not in CFG["bowler_wickets"] and "Retire Out" not in CFG["bowler_wickets"]


def test_batter_dismissals_charged_once_to_dismissed_player(balls, bat):
    clean = balls[balls.clean]
    cost = clean[clean.is_wicket & ~clean.dismissal_type.isin(CFG["non_batter_cost_dismissals"])
                 & clean.dismissed_player_id.notna()]
    assert int(bat.out.sum()) == len(cost)
    a = bat[bat.out == 1].groupby("player_id").size().sort_index()
    b = cost.groupby(cost.dismissed_player_id.astype(int)).size().sort_index()
    assert a.equals(b.rename_axis("player_id")) or (a.values == b.values).all()


def test_slots_equal_legal_balls(balls, bowl):
    assert len(bowl) == int(balls[balls.clean].legal.sum())




def test_calibrated_expected_wicket_candidate_reuses_its_pilot_model(monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "expected_stage", os.path.join(ROOT, "src", "05_expected.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    pilot = object()
    def unexpected_refit(*args, **kwargs):
        raise AssertionError("calibrated pilot must be reused, not refit")
    monkeypatch.setattr(module.lgb, "LGBMClassifier", unexpected_refit)
    selected = module._binary_model_for_fold(
        pilot, object(), np.zeros((2, 1)), np.array([0, 1]),
        np.array([True, False]), {})
    assert selected is pilot


def test_expected_wicket_credit_uses_fold_local_phase_mean_baseline():
    metrics = T("expected_model_metrics.csv").set_index("model")
    bat_rows = pd.read_parquet(os.path.join(INTERIM, "bat_rows.parquet"))
    bowl_rows = pd.read_parquet(os.path.join(INTERIM, "bowl_rows.parquet"))
    for role, d in [("batter", bat_rows), ("bowler", bowl_rows)]:
        selected = metrics.loc[f"{role} xWkt"]
        candidate = metrics.loc[f"{role} xWkt candidate"]
        assert selected.selected_method == "fold_local_phase_mean"
        assert np.isclose(selected.oof, selected.phase_mean_baseline, atol=1e-9)
        assert d.x_wkt.notna().all() and d.x_wkt.between(0, 1).all()
        assert d.x_wkt_model.notna().all() and d.x_wkt_model.between(0, 1).all()
        assert np.isfinite(candidate.oof)

def test_expected_models_are_centred(bat, bowl):
    f = bat[bat.faced == 1]
    assert abs((f.runs - f.x_runs).mean()) < 0.01
    assert abs((bowl.bowler_runs - bowl.x_runs).mean()) < 0.01


# ---- identity and lists -----------------------------------------------------------------------------------
def test_player_ids_resolve_to_one_name():
    mp = raw("competition_team_player_mapping")
    assert (mp.groupby("player_id").player_name.nunique() == 1).all()


@pytest.mark.parametrize("label", ["batter", "bowler"])
def test_top10_lists(label):
    mp = raw("competition_team_player_mapping")
    t = T(f"top10_{label}s.csv")
    assert len(t) == 10 and t.player_id.is_unique and t.dropdown_name.is_unique
    assert list(t.final_rank) == list(range(1, 11))
    name_of = mp.drop_duplicates("player_id").set_index("player_id").player_name
    assert (t.dropdown_name.values == name_of.loc[t.player_id].values).all()
    full = T(f"{label}_ratings.csv")
    assert full.player_id.is_unique
    assert set(t.player_id) <= set(full.player_id)


@pytest.mark.parametrize("label", ["batter", "bowler"])
def test_top10_players_meet_eligibility(label):
    t = T(f"top10_{label}s.csv")
    e = CFG["eligibility"]
    pre = "bat" if label == "batter" else "bowl"
    min_innings = e[f"{pre}_min_pressure_{'innings' if pre == 'bat' else 'spells'}"]
    assert (t.n_press_balls >= e[f"{pre}_min_pressure_balls"]).all()
    assert (t.n_press_innings >= min_innings).all()
    assert (t.n_total_balls >= e["min_total_balls"]).all()


@pytest.mark.parametrize("role,label", [("bat", "batter"), ("bowl", "bowler")])
def test_ratings_reproduce_from_credit_tables(role, label, bat, bowl):
    """Recompute the primary rating from the credit table and compare with the stored table."""
    import json
    from ratings_lib import Prep, rate, composite
    d = bat if role == "bat" else bowl
    lam = json.load(open(os.path.join(INTERIM, "lambdas.json")))[role]
    prep = Prep(d, role, pcol="pA")
    t = composite(rate(prep, lam["lambda_main"], lam["lambda_delta"]), prep.eligible())
    stored = T(f"{label}_ratings.csv").sort_values("rank")
    assert list(t.player_id.values[:10]) == list(stored.player_id.values[:10])
    assert np.allclose(t.rating.values, stored.rating.values, atol=1e-5)


# ---- text hygiene ---------------------------------------------------------------------------------------------
BANNED = re.compile(r"co-authored-by|generated with|claude|anthropic|chatgpt|openai|\bcopilot\b", re.I)


@pytest.mark.parametrize("fname", ["README.md", os.path.join("docs", "FINDINGS.md")])
def test_no_em_dashes_or_ai_attribution_in_docs(fname):
    path = os.path.join(ROOT, fname)
    if not os.path.exists(path):
        pytest.skip(f"{fname} not written yet")
    txt = open(path, encoding="utf-8").read()
    assert "—" not in txt, "em dash found"
    if fname.endswith("FINDINGS.md"):
        assert not BANNED.search(txt)


def test_no_ai_attribution_in_commit_messages():
    try:
        log = subprocess.run(["git", "log", "--format=%B"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except Exception:
        pytest.skip("git history not available")
    assert "—" not in log
    assert not BANNED.search(log)


# ---- phase 3 ----------------------------------------------------------------------------------------
def test_rating_uses_the_preregistered_task_composite():
    w = CFG["composite_weights"]
    spec = CFG["composite_weights_spec"]
    assert w == spec == {"level": 0.40, "impact": 0.25, "consistency": 0.20, "delta": 0.15}
    assert abs(sum(w.values()) - 1.0) < 1e-9
    assert CFG["ridge"]["lev_alpha"] == 1.0


@pytest.mark.parametrize("label", ["batter", "bowler"])
def test_primary_rating_is_the_weighted_sum_of_all_four_components(label):
    ratings = T(f"{label}_ratings.csv")
    expected = sum(CFG["composite_weights"][component] * ratings[f"z_{component}"]
                   for component in ("level", "impact", "consistency", "delta"))
    assert np.allclose(ratings.rating, expected, atol=1e-5)


def test_v3_predictive_challenger_is_reported_separately():
    comparison = pd.read_csv(os.path.join(V3, "final_comparison.csv"))
    assert set(comparison.role) == {"bat", "bowl"}
    assert set(comparison.trials) == {"tuning trials", "confirmation trials"}
    assert np.isfinite(comparison.gain).all()


def test_earlier_results_are_preserved():
    for d in ("phase1", "phase2"):
        for f in ("top10_batters.csv", "top10_bowlers.csv"):
            assert os.path.exists(os.path.join(ROOT, "outputs", d, f))


# ---- v2 ---------------------------------------------------------------------------------------------
V2 = os.path.join(ROOT, "outputs", "v2")


@pytest.mark.parametrize("label", ["batters", "bowlers"])
def test_v2_top10_lists(label):
    mp = raw("competition_team_player_mapping")
    t = pd.read_csv(os.path.join(V2, f"top10_{label}.csv"))
    assert len(t) == 10 and t.player_id.is_unique and list(t.final_rank) == list(range(1, 11))
    name_of = mp.drop_duplicates("player_id").set_index("player_id").player_name
    assert (t.dropdown_name.values == name_of.loc[t.player_id].values).all()
    full = pd.read_csv(os.path.join(V2, f"ratings_{label}.csv"))
    assert full.player_id.is_unique and (full.n_press_balls >= 40).all() and (full.n_total_balls >= 150).all()
    assert (t.rating.values[:-1] >= t.rating.values[1:]).all()
    assert (t.boot_rating_p10 <= t.rating).all() and (t.rating <= t.boot_rating_p90).all()


@pytest.mark.parametrize("label,role", [("batters", "bat"), ("bowlers", "bowl")])
def test_v2_final_rating_applies_the_selected_score_variant(label, role):
    chosen = json.load(open(os.path.join(V2, "chosen_config.json")))[role]
    ratings = pd.read_csv(os.path.join(V2, f"ratings_{label}.csv"))
    assert ratings.rating_score.eq(chosen["score"]).all()
    if chosen["score"] == "nrae":
        expected = ratings.nrae_per100_shrunk
    elif chosen["score"] == "wpa":
        expected = ratings.wpa_per100_shrunk
    elif chosen["score"].startswith("blend"):
        beta = float(chosen["score"].replace("blend", ""))
        z_n = (ratings.nrae_per100_shrunk - ratings.nrae_per100_shrunk.mean()) / ratings.nrae_per100_shrunk.std()
        z_w = (ratings.wpa_per100_shrunk - ratings.wpa_per100_shrunk.mean()) / ratings.wpa_per100_shrunk.std()
        expected = z_n + beta * z_w
    else:
        raise AssertionError(f"Unsupported V2 score: {chosen['score']}")
    assert np.allclose(ratings.rating, expected, atol=1e-5)


def test_v2_beats_naive_statistics_on_confirmation_trials():
    c = pd.read_csv(os.path.join(V2, "confirm.csv"))
    c = c[c.trials == "confirmation trials"]
    for role, naive in [("bat", ["raw strike rate", "raw NRAE"]), ("bowl", ["raw economy (negated)", "raw NRAE"])]:
        d = c[c.role == role].set_index("method")
        for n in naive:
            assert d.loc["v2 chosen", "objective"] > d.loc[n, "objective"]
        assert d.loc["v2 chosen", "objective"] >= d.loc["reference", "objective"] - 1e-9


def test_v2_adoption_rule_respected():
    log = pd.read_csv(os.path.join(V2, "search_log.csv"))
    chosen = pd.read_json(os.path.join(V2, "chosen_config.json"))
    for role in ("bat", "bowl"):
        cfg = chosen[role]["cfg"]
        ref = dict(half_life=24.0, alpha=1.0, assoc_w=0.5, lam=3000.0, role_prior=False, opp_adjust=True)
        for k, v in ref.items():
            cv = cfg[k]
            if (cv is None and v is None) or cv == v:
                continue
            rows = log[(log.role == role) & (log.option == k)]
            assert (rows.z > 2).any(), f"{role}.{k} moved without evidence"


# ---- v3 (final) ---------------------------------------------------------------------------------------
V3 = os.path.join(ROOT, "outputs", "v3")


@pytest.mark.parametrize("label", ["batters", "bowlers"])
def test_v3_top10_lists(label):
    mp = raw("competition_team_player_mapping")
    t = pd.read_csv(os.path.join(V3, f"top10_{label}.csv"))
    assert len(t) == 10 and t.player_id.is_unique and list(t.final_rank) == list(range(1, 11))
    name_of = mp.drop_duplicates("player_id").set_index("player_id").player_name
    assert (t.dropdown_name.values == name_of.loc[t.player_id].values).all()
    full = pd.read_csv(os.path.join(V3, f"ratings_{label}.csv"))
    assert full.player_id.is_unique and (full.n_press_balls >= 40).all() and (full.n_total_balls >= 150).all()
    assert (t.rating.values[:-1] >= t.rating.values[1:]).all()
    assert np.allclose(full.rating, full.runs_part + full.wicket_part, atol=1e-3)  # CSV keeps 6 significant figures
    assert full.boot_rating_p10.notna().all() and (full.boot_rating_p10 <= full.boot_rating_p90).all()


def test_v3_legacy_confirmation_is_reported_as_diagnostic_only():
    fc = pd.read_csv(os.path.join(V3, "final_comparison.csv"))
    assert set(fc.trials) == {"tuning trials", "confirmation trials"}
    assert np.isfinite(fc.gain).all()
    st = pd.read_csv(os.path.join(V3, "structure.csv"))
    assert "selection_basis" in st.columns
    assert (st.selection_basis == "tuning_only").all()
    assert (~st.confirmation_used_for_selection).all()


def test_v3_changes_have_evidence():
    st = pd.read_csv(os.path.join(V3, "structure.csv")).set_index(["role", "candidate"])
    assert ("bat", "inter pace lam 3000") in st.index
    assert ("bowl", "lam_wkt x10") in st.index
    assert st.loc[("bat", "inter pace lam 3000"), "selection_basis"] == "tuning_only"
    assert st.loc[("bowl", "lam_wkt x10"), "selection_basis"] == "tuning_only"
    import json
    ch = json.load(open(os.path.join(V3, "chosen_config.json")))
    assert ch["bat"]["inter"] == "pace" and ch["bat"]["credit"] == "bat_credit_v3"
    assert ch["bowl"]["lam_wkt"] == 10 * ch["bowl"]["lam"] and ch["bowl"]["credit"] == "bowl_credit"


# ---- remediation audits ---------------------------------------------------------------------------
def test_data_quality_has_no_unresolved_failures():
    quality = T("data_quality.csv")
    assert not quality.status.isin(["FAIL", "DIFFERS"]).any()
    integrity = T("audit_integrity.csv")
    assert not integrity.status.eq("FAIL").any()


def test_target_reconstruction_provenance_is_exported():
    audit = T("target_reconstruction_audit.csv")
    detail = T("target_reconstruction_by_match.csv")
    assert len(audit) > 0 and len(detail) > 0
    assert {"tot_1", "target_recon", "target", "target_source", "calibration_method",
            "calibration_training_matches", "calibration_max_training_date"}.issubset(detail.columns)
    assert detail.target_source.eq("first_innings_ball_reconstruction").all()
    assert np.allclose(detail.target, np.rint(detail.tot_1) + 1.0)
    assert not {"target_anchored", "target_adjustment_runs", "res_n", "tot_2"}.intersection(detail.columns)
    trained = detail[detail.calibration_method == "expanding_lad"]
    assert (pd.to_datetime(trained.calibration_max_training_date) <
            pd.to_datetime(trained.match_date)).all()


def test_playing_eleven_anomalies_have_reconcilable_detail():
    missing = T("playing_eleven_missing_strikers.csv")
    duplicates = T("playing_eleven_duplicates.csv")
    integrity = T("audit_integrity.csv").set_index("check")
    assert int(missing.missing_striker_balls.sum()) == int(integrity.loc["striker absent from playing_eleven (info only)", "observed"])
    assert missing.mapping_team_agrees.all()
    assert int(integrity.loc["missing XI striker references unresolved by competition roster", "observed"]) == 0
    assert int(duplicates.groupby(["match_id", "team_id", "player_id"]).size().sub(1).sum()) == int(
        integrity.loc["duplicate rows in playing_eleven (info only)", "observed"])
    assert int(integrity.loc["duplicate XI memberships assigned to multiple teams", "observed"]) == 0


def test_verified_ball_identity_source_override_is_applied():
    balls = pd.read_parquet(os.path.join(INTERIM, "balls.parquet"))
    row = balls[(balls.match_id == 37086) & (balls.innings == 1) &
                (balls.innings_ball_num == 111)].iloc[0]
    assert int(row.striker_id) == 3550
    assert int(row.non_striker_id) == 3543
    overrides = T("source_override_audit.csv")
    assert len(overrides) == 1
    assert int(overrides.iloc[0].corrected_non_striker_id) == 3543
    integrity = T("audit_integrity.csv").set_index("check")
    assert int(integrity.loc["striker equals non-striker in clean matches", "observed"]) == 0


def test_source_edge_case_anomalies_have_row_level_audits():
    integrity = T("audit_integrity.csv").set_index("check")
    identity = T("striker_non_striker_identity_collisions.csv")
    over_limit = T("bowler_over_limit.csv")
    assert len(identity) == int(integrity.loc["striker equals non-striker (info only)", "observed"])
    assert len(over_limit) == int(integrity.loc["bowler with more than 24 legal balls in an innings (info only)", "observed"])
    over_detail = T("bowler_over_limit_deliveries.csv")
    assert len(over_detail) == int(over_limit.legal_balls.sum())


def test_temporal_validation_is_forward_only_at_rating_layer():
    expected_folds = T("expected_fold_audit.csv")
    assert (expected_folds.future_train_matches <= expected_folds.train_matches).all()
    forward = expected_folds[expected_folds.fold >= 0]
    assert (pd.to_datetime(forward.train_max_date) < pd.to_datetime(forward.test_min_date)).all()
    assert (forward.future_train_matches == 0).all()
    tv = pd.read_csv(os.path.join(V3, "temporal_validation.csv"))
    assert len(tv) >= 8
    assert (tv.future_train_matches <= tv.n_train_matches).all()
    assert (pd.to_datetime(tv.train_max_date) < pd.to_datetime(tv.test_min_date)).all()
    assert (tv.future_train_matches == 0).all()
    assert tv.upstream_temporal_status.eq("chronologically_crossfit").all()


def test_v3_rr_fit_uses_v3_ratings():
    out = os.path.join(V3, "rr_fit", "rr_fit.csv")
    fit = pd.read_csv(out)
    assert set(fit.group) == {"batter", "bowler"}
    assert fit.rating.notna().all()


def test_v3_ratings_expose_descriptive_uplift_without_changing_score():
    for label in ("batters", "bowlers"):
        full = pd.read_csv(os.path.join(V3, f"ratings_{label}.csv"))
        assert "raw_pressure_uplift" in full.columns
        assert "press_innings_nrae_mad" in full.columns
        assert np.allclose(full.rating, full.runs_part + full.wicket_part, atol=1e-3)
