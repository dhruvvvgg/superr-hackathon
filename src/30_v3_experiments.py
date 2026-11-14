"""V3 experiments: structural model variants and ensembles, judged on the same held-out trials as V2.

Every candidate is scored on forward-only tuning and confirmation windows defined in 20_v2_search.py.
Paired differences are reported against the V2 configuration. Adoption uses tuning windows only (> 2 SE).
The legacy confirmation trials are descriptive diagnostics, not an untouched holdout: earlier V3 iterations
used them for candidate gating, so they must not be presented as independent final validation.
Usage: python src/30_v3_experiments.py <round_name> ; candidates are defined per round below.
Output: outputs/v3/<round>.csv
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import importlib.util
import json
import multiprocessing as mp
import sys

import numpy as np
import pandas as pd

from common import PROCESSED, ROOT
from v2_lib import pressure_stats, wspearman
from v3_lib import fit3

spec = importlib.util.spec_from_file_location("s20", os.path.join(os.path.dirname(__file__), "20_v2_search.py"))
s20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s20)
OUT = os.path.join(ROOT, "outputs", "v3")
os.makedirs(OUT, exist_ok=True)
_G = {}


def trial_sets(df):
    """Forward-only trial windows matching the V2 tuning and confirmation periods."""
    dd = pd.to_datetime(df.match_date)
    out = []
    windows = [("tune", c, 6) for c in s20.TUNE_CUTS] + [
        ("conf", c, months) for c, months in s20.CONF_CUTS
    ]
    for kind, cut_text, months in windows:
        cut = pd.Timestamp(cut_text)
        train = (dd < cut).values
        test = ((dd >= cut) & (dd < cut + pd.DateOffset(months=months))).values
        if not train.any() or not test.any():
            raise ValueError(f"{kind} temporal window {cut_text} has an empty train or test set")
        train_dates = pd.to_datetime(df.loc[train, "match_date"])
        test_dates = pd.to_datetime(df.loc[test, "match_date"])
        if train_dates.max() >= test_dates.min():
            raise AssertionError(f"{kind} temporal window {cut_text} contains future training data")
        out.append((kind, train, test, cut, 20))
    return out


def zs(s):
    return (s - s.mean()) / s.std()


def run_trial(i):
    df, role, cands, ens = _G["df"], _G["role"], _G["cands"], _G["ens"]
    kind, trm, tem, anchor, min_test = _G["trials"][i]
    tr, te = df[trm], df[tem]
    st_tr, st_te = pressure_stats(tr, role), pressure_stats(te, role)
    elig = st_tr[st_tr.unit >= 40].index
    tg = st_te[st_te.unit >= min_test]
    common = elig.intersection(tg.index)
    scores = {}
    for name, cfg in cands.items():
        key = tuple(sorted((k, str(v)) for k, v in cfg.items() if not k.startswith("_")))
        if key not in _G.setdefault("_cache", {}):
            _G["_cache"] = {k: v for k, v in _G["_cache"].items() if k[0] == i} if False else _G["_cache"]
        f = _G["_cache"].get((i, key))
        if f is None:
            f = fit3(tr, role, anchor, **{k: v for k, v in cfg.items() if not k.startswith("_")}).set_index("player_id").loc[common]
            _G["_cache"][(i, key)] = f
        sc = f.s_runs + cfg.get("_gamma", 1.0) * f.s_wkt
        if cfg.get("_blend"):
            sc = zs(sc) + cfg["_blend"] * zs(f.s_wpa)
        scores[name] = sc
    for name, members in ens.items():
        scores[name] = sum(zs(scores[m]) for m in members) / len(members)
    ww = tg.loc[common, "unit"].values
    train_dates = pd.to_datetime(tr.match_date)
    test_dates = pd.to_datetime(te.match_date)
    temporal = bool(len(train_dates) and len(test_dates) and train_dates.max() < test_dates.min())
    res = {"kind": kind, "n": len(common), "temporal": temporal,
           "train_max_date": train_dates.max().date().isoformat() if len(train_dates) else "",
           "test_min_date": test_dates.min().date().isoformat() if len(test_dates) else "",
           "test_max_date": test_dates.max().date().isoformat() if len(test_dates) else ""}
    for name, s in scores.items():
        res[name] = 0.5 * (wspearman(s.values, tg.loc[common, "nrae100"].values, ww) +
                           wspearman(s.values, tg.loc[common, "wpa100"].values, ww))
    return res


def evaluate(role, df, cands, ens, base="base"):
    _G.update(df=df, role=role, cands=cands, ens=ens, trials=trial_sets(df))
    with mp.get_context("fork").Pool(4) as pool:
        res = pool.map(run_trial, range(len(_G["trials"])))
    R = pd.DataFrame(res)
    R.to_csv(os.path.join(OUT, f"_trials_{_G.get('rnd', 'x')}_{os.environ.get('SUPERR_TAG', 'main')}_{role}.csv"), index=False)
    rows = []
    for name in list(cands) + list(ens):
        row = dict(role=role, candidate=name, selection_basis="tuning_only",
                   confirmation_used_for_selection=False)
        for kind in ("tune", "conf"):
            sub = R[R.kind == kind]
            dif = sub[name] - sub[base]
            row[f"{kind}_mean"] = sub[name].mean()
            row[f"{kind}_diff"] = dif.mean()
            row[f"{kind}_se"] = dif.std() / np.sqrt(len(dif)) if dif.std() > 0 else 0.0
            row[f"{kind}_z"] = row[f"{kind}_diff"] / row[f"{kind}_se"] if row[f"{kind}_se"] > 0 else 0.0
        row["passes"] = bool(row["tune_z"] > 2)
        rows.append(row)
    return pd.DataFrame(rows)


def round_structure(role, base):
    c = {"base": base}
    lam = base["lam"]
    for f in (0.15, 0.3, 0.5):
        c[f"floor {f}"] = dict(base, floor=f)
    for m in (0.3, 3.0, 10.0, 30.0):
        c[f"lam_wkt x{m:g}"] = dict(base, lam_wkt=lam * m)
    for m in (0.3, 3.0):
        c[f"lam_opp x{m:g}"] = dict(base, lam_opp=lam * m)
    inter = "pace" if role == "bat" else "lhb"
    for li in (3000.0, 10000.0, 30000.0):
        c[f"inter {inter} lam {li:g}"] = dict(base, inter=inter, lam_inter=li)
        c[f"inter death lam {li:g}"] = dict(base, inter="death", lam_inter=li)
    c["cap 3"] = dict(base, cap=3.0)
    c["cap 30"] = dict(base, cap=30.0)
    ens = {}
    c["alpha 0.5"] = dict(base, alpha=0.5)
    c["alpha 1.5"] = dict(base, alpha=1.5)
    c["alpha 0"] = dict(base, alpha=0.0)
    hl = base["half_life"]
    if hl:
        c["half-life x0.5"] = dict(base, half_life=hl * 0.5)
        c["half-life x2"] = dict(base, half_life=hl * 2)
    else:
        c["half-life 48"] = dict(base, half_life=48.0)
        c["half-life 24"] = dict(base, half_life=24.0)
    hls = [k for k in c if k.startswith("half-life")]
    ens["ens alpha 0.5/1/1.5"] = ["base", "alpha 0.5", "alpha 1.5"]
    ens["ens alpha 0/1"] = ["base", "alpha 0"]
    ens["ens half-lives"] = ["base"] + hls
    ens["ens alpha x half-life"] = ["base", "alpha 0.5", "alpha 1.5"] + hls
    return c, ens


def round_combine(role, base):
    lam = base["lam"]
    c = {"v2 base": dict(base)}
    if role == "bat":
        b2 = dict(base, inter="pace", lam_inter=3000.0)
        c["base"] = b2
        for li in (1000.0, 2000.0, 5000.0):
            c[f"inter pace lam {li:g}"] = dict(b2, lam_inter=li)
        for cap in (3.0, 5.0):
            c[f"+ cap {cap:g}"] = dict(b2, cap=cap)
        c["+ lam_wkt x3"] = dict(b2, lam_wkt=lam * 3)
        c["+ half-life 48"] = dict(b2, half_life=48.0)
        c["+ lam x0.5"] = dict(b2, lam=lam * 0.5, lam_inter=1500.0)
        c["+ lam x2"] = dict(b2, lam=lam * 2, lam_inter=6000.0)
    else:
        b2 = dict(base, lam_wkt=lam * 10)
        c["base"] = b2
        for m in (5.0, 20.0):
            c[f"lam_wkt x{m:g}"] = dict(b2, lam_wkt=lam * m)
        c["+ alpha 1.5"] = dict(b2, alpha=1.5)
        c["+ alpha 0.5"] = dict(b2, alpha=0.5)
        c["+ cap 3"] = dict(b2, cap=3.0)
        c["+ inter death 10000"] = dict(b2, inter="death", lam_inter=10000.0)
        c["+ inter lhb 10000"] = dict(b2, inter="lhb", lam_inter=10000.0)
        c["+ lam x0.5"] = dict(b2, lam=lam * 0.5, lam_wkt=lam * 5)
        c["+ lam x2"] = dict(b2, lam=lam * 2, lam_wkt=lam * 20)
        c["+ half-life 72"] = dict(b2, half_life=72.0)
    return c, {}


def round_score(role, base):
    lam = base["lam"]
    b2 = dict(base, inter="pace", lam_inter=3000.0) if role == "bat" else dict(base, lam_wkt=lam * 10)
    c = {"base": b2}
    for g in (0.5, 0.75, 1.25, 1.5):
        c[f"wicket part x{g:g}"] = dict(b2, _gamma=g)
    for bl in (0.1, 0.25, 0.5):
        c[f"+ WPA blend {bl:g}"] = dict(b2, _blend=bl)
    return c, {}


def round_baseonly(role, base):
    return {"base": base}, {}


def main(rnd):
    _G["rnd"] = rnd
    chosen = json.load(open(os.path.join(ROOT, "outputs", "v2", "chosen_config.json")))
    out = []
    for role, f in [("bat", "bat_credit"), ("bowl", "bowl_credit")]:
        df = pd.read_parquet(os.path.join(PROCESSED, f"{f}.parquet"))
        base = {k: v for k, v in chosen[role]["cfg"].items() if k not in ("role_prior",)}
        base.setdefault("floor", 0.05)
        cands, ens = ROUNDS[rnd](role, base)
        t = evaluate(role, df, cands, ens)
        out.append(t)
        print(t.round(4).to_string(index=False), flush=True)
    tag = os.environ.get("SUPERR_TAG", "")
    pd.concat(out).to_csv(os.path.join(OUT, f"{rnd}{'_' + tag if tag else ''}.csv"), index=False, float_format="%.5f")


ROUNDS = {"structure": round_structure, "baseonly": round_baseonly, "combine": round_combine, "score": round_score}

def run_all_rounds():
    """Every round that the V3 decisions rest on, in order. Rounds on the richer baseline run under the
    'xfeat' tag built by 31_v3_credit.py."""
    import subprocess
    for rnd, tag in [("structure", ""), ("combine", ""), ("score", ""), ("baseonly", ""), ("baseonly", "xfeat"), ("score", "xfeat")]:
        env = dict(os.environ, PYTHONWARNINGS="ignore")
        env.pop("SUPERR_TAG", None)
        if tag:
            env["SUPERR_TAG"] = tag
        r = subprocess.run([sys.executable, os.path.abspath(__file__), rnd], cwd=ROOT, env=env, stdout=subprocess.DEVNULL)
        if r.returncode:
            sys.exit(f"round {rnd} ({tag or 'main'}) failed")
        print(f"  round {rnd} on {tag or 'main'} credit done", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        run_all_rounds()
