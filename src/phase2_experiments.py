"""Phase 2b: run pipeline variants side by side and score each on model-quality evidence only.
Each variant lives in data/experiments/<tag>/ and never touches the main outputs.
Usage: python src/phase2_experiments.py [tag ...]   (no arguments = all variants)
Writes outputs/tables/phase2_experiments.csv."""
import json
import os
import shutil
import subprocess
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGES = ["01_profile", "02_build_state", "03_win_prob", "04_pressure", "05_expected", "06_attribution", "07_ratings"]
# tag: (overrides, first stage that must be re-run, tag to copy earlier stages from, reason)
VARIANTS = {
    "base": ({}, "01", None, "phase 1 primary specification"),
    "wp_gbm": ({"wp.model": "mono"}, "03", "base", "originally pre-registered monotone LightGBM win-probability model"),
    "wp_nomom": ({"wp.model": "respoly"}, "03", "base", "win probability without momentum features"),
    "lev_rms": ({"leverage.kind": "rms"}, "04", "base", "leverage as root-mean-square swing instead of mean absolute swing"),
    "role_aware": ({"baseline.role_aware": True}, "05", "base",
                   "baseline knows balls already faced by the striker and batting position"),
    "opp_ts": ({"ridge.opp_team_season": True}, "07", "base", "ridge adds an opposition-team-by-season strength term"),
    "prior_sd": ({"composite.standardise": "prior_sd"}, "07", "base",
                 "components scaled by between-player prior SD instead of z-scored after shrinkage"),
    "role_prior": ({"baseline.role_aware": True, "composite.standardise": "prior_sd"}, "07", "role_aware",
                   "role-aware baseline and prior-SD scaling together"),
    "role_prior_opp": ({"baseline.role_aware": True, "composite.standardise": "prior_sd", "ridge.opp_team_season": True},
                       "07", "role_aware", "role-aware baseline, prior-SD scaling and opposition term"),
}


def run(tag):
    ov, first, src, reason = VARIANTS[tag]
    dst = os.path.join(ROOT, "data", "experiments", tag)
    if src and not os.path.exists(os.path.join(dst, "tables", "quality.json")):
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(os.path.join(ROOT, "data", "experiments", src), dst)
    env = dict(os.environ, SUPERR_TAG=tag, SUPERR_OVERRIDES=json.dumps(ov), PYTHONWARNINGS="ignore")
    for s in STAGES + ["eval_quality"]:
        if s[:2].isdigit() and s[:2] < first:
            continue
        r = subprocess.run([sys.executable, os.path.join(ROOT, "src", f"{s}.py")], cwd=ROOT, env=env,
                           stdout=subprocess.DEVNULL)
        if r.returncode:
            sys.exit(f"{tag}: stage {s} failed")
    print(f"done {tag}", flush=True)


def collect():
    rows = []
    for tag, (ov, _, _, reason) in VARIANTS.items():
        p = os.path.join(ROOT, "data", "experiments", tag, "tables", "quality.json")
        if os.path.exists(p):
            rows.append(dict(json.load(open(p)), overrides=json.dumps(ov), reason=reason))
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(ROOT, "outputs", "tables", "phase2_experiments.csv"), index=False, float_format="%.5g")
    return t


if __name__ == "__main__":
    for tag in (sys.argv[1:] or list(VARIANTS)):
        run(tag)
    print(collect().T.to_string())
