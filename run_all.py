"""Run every stage in order from the raw CSVs. Usage: python run_all.py [first_stage]"""
import os
import subprocess
import sys
import time

STAGES = ["01_profile", "02_build_state", "03_win_prob", "04_pressure", "05_expected", "06_attribution",
          "07_ratings", "08_robustness", "09_rr_fit", "10_audit", "12_improve", "13_improve2", "11_report", "20_v2_search", "21_v2_rate", "22_v2_report"]


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    start = sys.argv[1] if len(sys.argv) > 1 else "01"
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONWARNINGS="ignore")
    t_all = time.time()
    skip = [s for s in STAGES if s[:2] == start[:2]]
    first = STAGES.index(skip[0]) if skip else 0
    for s in STAGES[first:]:
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.join(root, "src", f"{s}.py")], cwd=root, env=env)
        if r.returncode != 0:
            sys.exit(f"stage {s} failed with exit code {r.returncode}")
        print(f"== {s} finished in {time.time() - t0:.0f}s ==", flush=True)
    print(f"== pipeline finished in {(time.time() - t_all) / 60:.1f} min ==")


if __name__ == "__main__":
    main()
