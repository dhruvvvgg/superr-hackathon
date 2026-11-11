"""Stage 08: uncertainty and robustness.

1. Cluster bootstrap by match (config n_bootstrap resamples) of the full rating.
2. Sensitivity grid: structural configurations x (primary weights + Dirichlet weight draws).
3. Persistence: season split, odd/even split, random half splits.
4. Pre-registered decision rule and the final top-10 lists.
5. Face-validity audit.

Outputs: batter_ratings.csv / bowler_ratings.csv (updated with intervals), top10_batters.csv,
top10_bowlers.csv, sensitivity_membership.csv, sensitivity_configs.csv, persistence.csv,
face_validity.csv, decision_rule.csv and the figures listed in the handover.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import CFG, INTERIM, PROCESSED, TABLES, FIGURES, SEED, player_names, save_table, setup_matplotlib
from ratings_lib import Prep, rate, composite, COMPONENTS
from robust_lib import bootstrap, split_half, random_splits, dirichlet_weights

ROLES = [("bat", "bat_credit", "batter"), ("bowl", "bowl_credit", "bowler")]


def configs():
    weak = lambda d: (d.tier == "A-team") | ((d.tier == "T20I") & d.opp_assoc)
    c = [dict(name="A primary", family="primary")]
    for v, lab in [("B", "B contested-state rule"), ("C", "C leverage pct >= 90"), ("D", "D leverage pct >= 70"),
                   ("E", "E death overs, WP 0.2-0.8"), ("F", "F global leverage pct >= 80")]:
        c.append(dict(name=lab, family="pressure definition", pcol="p" + v))
    c.append(dict(name="eligibility x0.5", family="eligibility", scale=0.5))
    c.append(dict(name="eligibility x1.5", family="eligibility", scale=1.5))
    c.append(dict(name="recency off", family="weights", prep_kw=dict(use_recency=False)))
    c.append(dict(name="A-team and associates at full weight", family="weights", prep_kw=dict(use_comp_weight=False)))
    c.append(dict(name="A-team and associate opposition removed", family="data subset", subset=lambda d: ~weak(d)))
    c.append(dict(name="IPL only", family="data subset", subset=lambda d: d.tier == "IPL"))
    c.append(dict(name="T20I only", family="data subset", subset=lambda d: d.tier == "T20I"))
    c.append(dict(name="empirical Bayes estimator", family="estimator", estimator="eb"))
    return c


def run_config(df, role, lam, cfg):
    d = df[cfg["subset"](df)] if "subset" in cfg else df
    prep = Prep(d, role, pcol=cfg.get("pcol", "pA"), **cfg.get("prep_kw", {}))
    elig = prep.eligible(cfg.get("scale", 1.0))
    t = composite(rate(prep, lam[0], lam[1]), elig, estimator=cfg.get("estimator", "ridge"))
    return t


def main():
    print("Stage 08: robustness")
    R = CFG["robustness"]
    names = player_names()
    lam_all = json.load(open(os.path.join(INTERIM, "lambdas.json")))
    W = dirichlet_weights(R["n_dirichlet"])
    pers_rows, cfg_rows, rule_rows, face_rows = [], [], [], []
    final = {}
    plt = setup_matplotlib()

    for role, fname, label in ROLES:
        df = pd.read_parquet(os.path.join(PROCESSED, f"{fname}.parquet"))
        lam = (lam_all[role]["lambda_main"], lam_all[role]["lambda_delta"])
        rt = pd.read_csv(os.path.join(TABLES, f"{label}_ratings.csv"))
        drop = [c for c in rt.columns if c.startswith(("boot_", "grid_", "final_"))]
        rt = rt.drop(columns=drop)
        prep = Prep(df, role, pcol="pA")
        elig = np.isin(prep.players, rt.player_id.values)

        # ---- 1. bootstrap ---------------------------------------------------------------------------
        ids, (rk, rating, delta, level) = bootstrap(prep, lam, elig, R["n_bootstrap"])
        boot = pd.DataFrame({"player_id": ids,
                             "boot_rank_mean": rk.mean(0), "boot_rank_p10": np.percentile(rk, 10, axis=0),
                             "boot_rank_p90": np.percentile(rk, 90, axis=0),
                             "boot_top10_prob": (rk <= 10).mean(0), "boot_top20_prob": (rk <= 20).mean(0),
                             "boot_rating_p10": np.percentile(rating, 10, axis=0),
                             "boot_rating_p90": np.percentile(rating, 90, axis=0),
                             "boot_delta_negative_prob": (delta < 0).mean(0)})
        rt = rt.merge(boot, on="player_id", how="left", validate="1:1")
        assert rt.boot_rank_mean.notna().all()
        print(f"  {label}: bootstrap done ({R['n_bootstrap']} resamples, {len(ids)} eligible players)")

        # ---- 2. sensitivity grid ------------------------------------------------------------------------
        prim = rt.set_index("player_id")
        memb = {}
        for cfg in configs():
            t = run_config(df, role, lam, cfg)
            Z = t[[f"z_{c}" for c in COMPONENTS]].values
            scores = Z @ W.T                                   # players x weight vectors
            order = np.argsort(-scores, axis=0)[:10]            # top-10 row indices per weight vector
            cnt = np.bincount(order.ravel(), minlength=len(t)) / W.shape[0]
            memb[cfg["name"]] = pd.Series(cnt, index=t.player_id.values)
            top_here = set(t.player_id.values[np.argsort(-scores[:, 0])[:10]])
            common = t.set_index("player_id").index.intersection(prim.index)
            cfg_rows.append(dict(role=label, config=cfg["name"], family=cfg["family"], n_eligible=len(t),
                                 top10_overlap_with_primary=len(top_here & set(prim[prim["rank"] <= 10].index)),
                                 spearman_with_primary=spearmanr(t.set_index("player_id").loc[common, "rating"],
                                                                 prim.loc[common, "rating"]).statistic,
                                 n_common=len(common)))
        M = pd.DataFrame(memb).fillna(0.0)
        M["grid_top10_prob"] = M.mean(axis=1)
        rt["grid_top10_prob"] = rt.player_id.map(M.grid_top10_prob).fillna(0.0)
        Mx = M.reset_index().rename(columns={"index": "player_id"})
        Mx.insert(1, "player_name", Mx.player_id.map(names))
        Mx.insert(2, "primary_rank", Mx.player_id.map(prim["rank"]))
        Mx.insert(3, "role", label)
        Mx = Mx[(Mx.grid_top10_prob > 0) | (Mx.primary_rank <= 20)].sort_values(
            ["grid_top10_prob", "primary_rank"], ascending=[False, True])
        final[f"memb_{label}"] = Mx

        # ---- 3. persistence -------------------------------------------------------------------------------
        minfo = df.drop_duplicates("match_id").sort_values(["match_date", "match_id"])
        mids = np.sort(df.match_id.unique())
        year = minfo.set_index("match_id").year.reindex(mids).values
        order_ = minfo.match_id.values
        odd = np.isin(mids, order_[::2])
        splits = {"season split (2022-24 vs 2025-26)": [year <= 2024], "odd/even match split": [odd],
                  f"random half splits (mean of {R['n_random_splits']})": random_splits(mids, R["n_random_splits"])}
        for sname, sp in splits.items():
            res = split_half(df, role, lam, sp)
            r = dict(role=label, split=sname, n_common=res.n_common.mean())
            for c in ["rating"] + COMPONENTS:
                r[f"spearman_{c}"] = res[c].mean()
                if len(res) > 1:
                    r[f"sd_{c}"] = res[c].std()
            r["spearman_brown_rating"] = 2 * r["spearman_rating"] / (1 + r["spearman_rating"])
            pers_rows.append(r)
            if sname.startswith("season"):
                # keep the two halves for the scatter figure
                halves = []
                for part in (mids[sp[0]], mids[~sp[0]]):
                    p2 = Prep(df[df.match_id.isin(part)], role)
                    halves.append(composite(rate(p2, lam[0], lam[1]), p2.eligible(0.5, require_recent=False)).set_index("player_id"))
                cm = halves[0].index.intersection(halves[1].index)
                final[f"scatter_{label}"] = (halves[0].loc[cm, "rating"], halves[1].loc[cm, "rating"])
        print(f"  {label}: persistence done")

        # ---- 4. decision rule -------------------------------------------------------------------------------
        rt = rt.sort_values("rank").reset_index(drop=True)
        thr = R["swap_threshold"]
        top = rt[rt["rank"] <= 10]
        weak_ = top[top.grid_top10_prob < thr]
        outsiders = rt[(rt["rank"] > 10) & (rt.grid_top10_prob >= thr)].sort_values("rank")
        keep = top[top.grid_top10_prob >= thr].player_id.tolist()
        n_swap = min(len(weak_), len(outsiders))
        swapped_out = weak_.sort_values("grid_top10_prob").head(n_swap)
        swapped_in = outsiders.head(n_swap)
        final_ids = [p for p in top.player_id if p not in set(swapped_out.player_id)] + swapped_in.player_id.tolist()
        final_tab = rt[rt.player_id.isin(final_ids)].sort_values("rank").reset_index(drop=True)
        final_tab.insert(0, "final_rank", np.arange(1, len(final_tab) + 1))
        rt["final_rank"] = rt.player_id.map(final_tab.set_index("player_id").final_rank)
        for _, r in weak_.iterrows():
            rule_rows.append(dict(role=label, player_id=r.player_id, player_name=r.player_name, primary_rank=r["rank"],
                                  grid_top10_prob=r.grid_top10_prob,
                                  action="swapped out" if r.player_id in set(swapped_out.player_id) else
                                  "below threshold, kept (no outsider at or above threshold)"))
        for _, r in swapped_in.iterrows():
            rule_rows.append(dict(role=label, player_id=r.player_id, player_name=r.player_name, primary_rank=r["rank"],
                                  grid_top10_prob=r.grid_top10_prob, action="swapped in"))
        if not len(weak_):
            rule_rows.append(dict(role=label, player_id="", player_name="", primary_rank="", grid_top10_prob="",
                                  action="no primary top-10 player below the threshold; primary list kept"))
        print(f"  {label}: decision rule, {len(weak_)} below {thr}, {n_swap} swapped")

        cols = ["final_rank", "player_id", "player_name", "rating", "boot_rating_p10", "boot_rating_p90", "rank",
                "boot_rank_mean", "boot_rank_p10", "boot_rank_p90", "boot_top10_prob", "grid_top10_prob",
                "z_level", "z_impact", "z_consistency", "z_delta", "level", "normal", "delta", "impact",
                "hit_rate", "downside", "n_press_balls", "n_press_innings", "n_total_balls",
                "press_share_weak_opp", "press_share_ipl", "ipl_2026_team", "national_team", "dips_under_pressure"]
        extra = ["press_sr", "normal_sr", "press_avg", "press_runs", "press_outs"] if role == "bat" else \
                ["press_econ", "normal_econ", "press_wkts", "press_sr", "press_dot_pct"]
        ft = final_tab[cols + extra].rename(columns={"rank": "primary_rank"})
        ft.insert(3, "dropdown_name", ft.player_name)
        save_table(ft, f"top10_{label}s.csv")
        lead = ["rank", "final_rank", "player_id", "player_name", "rating", "boot_rating_p10", "boot_rating_p90",
                "boot_rank_mean", "boot_rank_p10", "boot_rank_p90", "boot_top10_prob", "grid_top10_prob"]
        rt = rt[lead + [c for c in rt.columns if c not in lead]]
        save_table(rt, f"{label}_ratings.csv")
        final[label] = rt
        final[f"top_{label}"] = ft

        # ---- 5. face validity ----------------------------------------------------------------------------------
        all_desc = df[df.phase == "death"]
        vol = (all_desc[all_desc.faced == 1] if role == "bat" else all_desc).groupby("player_id").size() \
            .sort_values(ascending=False).head(15)
        pidx = {p: i for i, p in enumerate(prep.players)}
        for pid, n in vol.items():
            row = rt[rt.player_id == pid]
            i = pidx[pid]
            reason = ""
            if not len(row):
                e = CFG["eligibility"]; pre = "bat" if role == "bat" else "bowl"
                fails = []
                if prep.n_press[i] < e[f"{pre}_min_pressure_balls"]: fails.append(f"pressure balls {prep.n_press[i]}")
                if prep.n_press_inn[i] < e[f"{pre}_min_pressure_{'innings' if pre == 'bat' else 'spells'}"]: fails.append(f"pressure innings {prep.n_press_inn[i]}")
                if prep.n_total[i] < e["min_total_balls"]: fails.append(f"total balls {prep.n_total[i]}")
                if not prep.recent[i]: fails.append("no appearance in 2025 or 2026")
                reason = "not eligible: " + ", ".join(fails)
            face_rows.append(dict(role=label, player_id=pid, player_name=names[pid], death_over_balls=int(n),
                                  eligible=bool(len(row)), rank=row["rank"].iloc[0] if len(row) else np.nan,
                                  rating=row.rating.iloc[0] if len(row) else np.nan,
                                  z_level=row.z_level.iloc[0] if len(row) else np.nan,
                                  z_impact=row.z_impact.iloc[0] if len(row) else np.nan,
                                  z_consistency=row.z_consistency.iloc[0] if len(row) else np.nan,
                                  z_delta=row.z_delta.iloc[0] if len(row) else np.nan,
                                  boot_top10_prob=row.boot_top10_prob.iloc[0] if len(row) else np.nan,
                                  n_press_balls=int(prep.n_press[i]), note=reason))

    save_table(pd.concat([final["memb_batter"], final["memb_bowler"]]), "sensitivity_membership.csv")
    save_table(pd.DataFrame(cfg_rows), "sensitivity_configs.csv")
    save_table(pd.DataFrame(pers_rows), "persistence.csv")
    save_table(pd.DataFrame(rule_rows), "decision_rule.csv")
    save_table(pd.DataFrame(face_rows), "face_validity.csv")
    print(pd.DataFrame(pers_rows)[["role", "split", "n_common", "spearman_rating", "spearman_level", "spearman_impact",
                                   "spearman_consistency", "spearman_delta"]].round(3).to_string())

    # ---- figures ----------------------------------------------------------------------------------------------
    for label, color in [("batter", "#1f6fb2"), ("bowler", "#2a9d8f")]:
        ft = final[f"top_{label}"].iloc[::-1]
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.barh(ft.player_name, ft.rating, color=color, alpha=0.85)
        ax.errorbar(ft.rating, ft.player_name, xerr=[np.maximum(ft.rating - ft.boot_rating_p10, 0), np.maximum(ft.boot_rating_p90 - ft.rating, 0)],
                    fmt="none", ecolor="black", capsize=4, lw=1.5)
        for y_, (r_, p_) in enumerate(zip(ft.boot_rating_p90, ft.boot_top10_prob)):
            ax.text(r_ + 0.05, y_, f"P(top 10) {p_:.2f}", va="center", fontsize=10)
        ax.set_xlabel("Composite pressure rating (z-score units), bars = 80% bootstrap interval")
        ax.set_title(f"Top 10 {label}s under pressure")
        ax.set_xlim(left=min(0, ft.boot_rating_p10.min() - 0.1), right=ft.boot_rating_p90.max() + 1.0)
        fig.tight_layout(); fig.savefig(os.path.join(FIGURES, f"top10_{label}s.png")); plt.close(fig)

        Mx = final[f"memb_{label}"].head(20)
        cols = [c["name"] for c in configs()] + ["grid_top10_prob"]
        fig, ax = plt.subplots(figsize=(13, 8))
        im = ax.imshow(Mx[cols].values, cmap="Blues", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(cols))); ax.set_xticklabels([c.replace("grid_top10_prob", "ALL CONFIGS") for c in cols], rotation=40, ha="right")
        ax.set_yticks(range(len(Mx))); ax.set_yticklabels([f"{n} (#{int(r) if r == r else '-'})" for n, r in zip(Mx.player_name, Mx.primary_rank)])
        for i in range(len(Mx)):
            for j, c in enumerate(cols):
                v = Mx[c].values[i]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8, color="white" if v > 0.6 else "black")
        ax.grid(False)
        ax.set_title(f"Top-10 membership frequency across the sensitivity grid: {label}s (primary rank in brackets)")
        fig.colorbar(im, ax=ax, fraction=0.025)
        fig.tight_layout(); fig.savefig(os.path.join(FIGURES, f"sensitivity_heatmap_{label}s.png")); plt.close(fig)

        rt = final[label]
        t20 = rt[rt["rank"] <= 20]
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.scatter(rt.normal, rt.level, s=14, color="lightgrey", label="all eligible")
        ax.scatter(t20.normal, t20.level, s=40, color=color, label="top 20")
        lim = [min(rt.normal.min(), rt.level.min()) - 1, max(rt.normal.max(), rt.level.max()) + 1]
        ax.plot(lim, lim, color="grey", ls="--", lw=1, label="pressure = normal")
        for _, r in t20.iterrows():
            ax.annotate(r.player_name, (r.normal, r.level), fontsize=8, xytext=(4, 3), textcoords="offset points")
        ax.set_xlabel("Normal level (NRAE per 100 balls, shrunk, opponent-adjusted)")
        ax.set_ylabel("Pressure level (normal + pressure delta)")
        ax.set_title(f"Pressure level versus normal level: {label}s (above the line = lifts under pressure)")
        ax.legend(frameon=False, loc="upper left")
        fig.tight_layout(); fig.savefig(os.path.join(FIGURES, f"level_vs_normal_{label}s.png")); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    pers = pd.DataFrame(pers_rows)
    for ax, (label, color) in zip(axes, [("batter", "#1f6fb2"), ("bowler", "#2a9d8f")]):
        a, b_ = final[f"scatter_{label}"]
        ax.scatter(a, b_, s=22, color=color, alpha=0.8)
        rho = pers[(pers.role == label) & pers.split.str.startswith("season")].spearman_rating.iloc[0]
        ax.set_title(f"{label.capitalize()}s: Spearman {rho:.2f} (n={len(a)})")
        ax.set_xlabel("Rating from 2022-2024 matches"); ax.set_ylabel("Rating from 2025-2026 matches")
        ax.axhline(0, color="grey", lw=0.8); ax.axvline(0, color="grey", lw=0.8)
    fig.suptitle("Persistence of the pressure rating across seasons")
    fig.tight_layout(); fig.savefig(os.path.join(FIGURES, "persistence_scatter.png")); plt.close(fig)

    # ---- acceptance rows ---------------------------------------------------------------------------------------
    mp_names = set(pd.read_csv(os.path.join(os.path.dirname(TABLES), "..", "data", "raw",
                                            "competition_team_player_mapping.csv")).player_name)
    dq = pd.read_csv(os.path.join(TABLES, "data_quality.csv"))
    dq = dq[dq.stage != "08_robustness"]
    acc = []
    for label in ("batter", "bowler"):
        ft = final[f"top_{label}"]
        ok = ft.player_id.is_unique and len(ft) == 10 and ft.dropdown_name.isin(mp_names).all()
        acc.append(dict(stage="08_robustness", check=f"top-10 {label}s: 10 unique ids, every name in the mapping file",
                        claimed=True, observed=bool(ok), status="pass" if ok else "FAIL", note=""))
    save_table(pd.concat([dq, pd.DataFrame(acc)], ignore_index=True), "data_quality.csv")


if __name__ == "__main__":
    main()
