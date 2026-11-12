"""V3 stage A: credit tables with the richer situational baseline for batters (phase 4 evidence:
outputs/v3/). Runs stages 05 and 06 in an isolated directory (data/experiments/xfeat) and copies the batter
credit table to data/processed/bat_credit_v3.parquet. The main credit tables are not touched."""
import json
import os
import shutil
import subprocess
import sys

from common import ROOT

TAG = "xfeat"


def main():
    print("V3 stage A: richer-baseline batter credit")
    d = os.path.join(ROOT, "data", "experiments", TAG)
    shutil.rmtree(d, ignore_errors=True)
    for sub in ("processed", "tables", "figures"):
        os.makedirs(os.path.join(d, sub))
    shutil.copytree(os.path.join(ROOT, "data", "interim"), os.path.join(d, "interim"))
    env = dict(os.environ, SUPERR_TAG=TAG, SUPERR_OVERRIDES=json.dumps({"baseline.extra_feats": True}), PYTHONWARNINGS="ignore")
    for s in ("05_expected", "06_attribution"):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "src", f"{s}.py")], cwd=ROOT, env=env, stdout=subprocess.DEVNULL)
        if r.returncode:
            sys.exit(f"{s} failed")
    shutil.copy(os.path.join(d, "processed", "bat_credit.parquet"), os.path.join(ROOT, "data", "processed", "bat_credit_v3.parquet"))
    print("  wrote data/processed/bat_credit_v3.parquet")


if __name__ == "__main__":
    main()
