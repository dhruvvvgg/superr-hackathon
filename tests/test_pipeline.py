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


def test_extras_calibration_no_worse_than_one_run_rule():
    c = T("extras_calibration.csv").set_index("item").fitted
    assert c["margin MAE (runs), fitted"] <= c["margin MAE (runs), simple"] + 1e-9


def test_chase_end_state_consistent_with_result(balls, minfo):
    """With the anchored target, a chase won by wickets ends at or past the target and a chase lost
    by N runs ends exactly N+1 short."""
    last = balls[(balls.innings == 2) & balls.clean].groupby("match_id").tail(1).set_index("match_id")
    end = last.score_before + last.total_runs
    mi = minfo.set_index("match_id").loc[last.index]
    w = mi.res_kind == "wkts"
    assert (end[w] >= last.target[w] - 1e-6).all()
    r = mi.res_kind == "runs"
    assert np.allclose(last.target[r] - end[r], mi.res_n[r] + 1)


# ---- win probability ---------------------------------------------------------------------------------
def test_wp_beats_state_free_baseline():
    m = T("wp_model_metrics.csv")
    p = m[(m.role == "primary") & (m["sample"] == "all")].log_loss.iloc[0]
    b = m[(m.role == "baseline") & (m["sample"] == "all")].log_loss.iloc[0]
    assert p < b - 0.1


def test_wp_calibrated_in_dense_bins():
    m = T("wp_model_metrics.csv")
    assert m[(m.role == "primary") & (m["sample"] == "all")].max_calib_gap_dense_bins.iloc[0] <= 0.03


def test_no_match_scored_by_a_model_that_saw_it():
    wp = pd.read_parquet(os.path.join(INTERIM, "wp.parquet"))
    assert (wp.groupby("match_id").fold.nunique() == 1).all()
    with open(os.path.join(INTERIM, "wp_models.pkl"), "rb") as f:
        pk = pickle.load(f)
    fm = pd.Series(pk["fold_map"])
    assert (wp.drop_duplicates("match_id").set_index("match_id").fold == fm.reindex(wp.match_id.unique())).all()
    assert wp.wp_before.between(0, 1).all()


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
    assert (t.n_press_balls >= e[f"{pre}_min_pressure_balls"]).all()
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
def test_rating_is_the_documented_phase3_choice():
    w = CFG["composite_weights"]
    assert w["level"] == 1.0 and w["impact"] == w["consistency"] == w["delta"] == 0.0
    assert CFG["ridge"]["lev_alpha"] == 1.0
    assert abs(sum(CFG["composite_weights_spec"].values()) - 1.0) < 1e-9


@pytest.mark.parametrize("role", ["bat", "bowl"])
def test_adopted_rating_beats_spec_composite_on_heldout_prediction(role):
    t = T("phase3_final_candidates.csv")
    t = t[t.role == role].set_index("candidate")
    assert t.loc["lev-level a=1", "d_nrae_vs_spec"] > 2 * t.loc["lev-level a=1", "d_nrae_se"]
    assert t.loc["lev-level a=1", "pred_nrae"] > t.loc["spec composite (phase 1-2)", "pred_nrae"]
    tt = T("phase3_temporal.csv").query("role == @role").set_index("candidate").pred_nrae_2025_26
    assert tt["lev-level a=1"] > tt["spec composite (phase 1-2)"]


def test_earlier_results_are_preserved():
    for d in ("phase1", "phase2"):
        for f in ("top10_batters.csv", "top10_bowlers.csv"):
            assert os.path.exists(os.path.join(ROOT, "outputs", d, f))
