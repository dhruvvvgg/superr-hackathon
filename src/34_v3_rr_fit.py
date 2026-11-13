"""V3 RR fit: reuse the established RR fit logic with the final V3 ratings and credit tables."""
import importlib.util
import os

from common import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location("rr_fit_stage", os.path.join(HERE, "09_rr_fit.py"))
RR_FIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RR_FIT)


def main():
    out = os.path.join(ROOT, "outputs", "v3", "rr_fit")
    RR_FIT.main(
        rating_dir=os.path.join(ROOT, "outputs", "v3"),
        out_dir=out,
        bat_credit_name="bat_credit_v3",
        bowl_credit_name="bowl_credit",
        figure_path=os.path.join(ROOT, "outputs", "v3", "rr_gap.png"),
        label="V3",
    )


if __name__ == "__main__":
    main()
