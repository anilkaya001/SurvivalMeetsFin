"""Background thread: model fitting and live scoring."""

import time
import traceback

from survival.config import REFRESH_S, HISTORY_CAP
from survival.data     import load_history
from survival.episodes import build_episodes
from survival.cox      import fit_cox
from survival.aft      import fit_aft
from survival.logrank  import pairwise_logrank, three_group_logrank
from survival.scoring  import score_live
from survival.config   import AFT_DISTRIBUTIONS

from .state import state, lock, refit_event, models


def full_fit(asset_ticker: str, risk_ticker: str) -> dict:
    print(f"  [FIT] Downloading {asset_ticker} / {risk_ticker} …")
    df  = load_history(asset_ticker, risk_ticker)
    print(f"  [FIT] {len(df):,} trading days.")

    edf  = build_episodes(df)
    n_ep = len(edf)
    n_ev = int(edf["event"].sum())
    print(f"  [FIT] {n_ep} episodes | {n_ev} events ({n_ev / max(n_ep, 1) * 100:.1f}%)")

    cox_result, lrt_stat, lrt_p, bch, z_params, c_index = fit_cox(edf)
    print(f"  [FIT] Cox  LRT chi2={lrt_stat:.2f}  p={lrt_p:.2e}  C={c_index:.3f}")

    aft_models = {}
    best_aic   = ("", 1e18)
    for dist in AFT_DISTRIBUTIONS:
        shape, sigma, beta, aic, bic = fit_aft(edf, dist=dist)
        aft_models[dist] = {
            "dist": dist, "shape": shape, "sigma": sigma,
            "beta": beta, "aic": round(aic, 1), "bic": round(bic, 1),
        }
        print(f"  [FIT] {dist.title():<12}  shape={shape:.3f}  AIC={aic:.1f}  BIC={bic:.1f}")
        if aic < best_aic[1]:
            best_aic = (dist, aic)

    pw_stat, pw_p = pairwise_logrank(edf)
    g3_stat, g3_p = three_group_logrank(edf)

    import numpy as np
    meta = {
        "n_ep":        n_ep,
        "n_ev":        n_ev,
        "breach_rate": round(n_ev / max(n_ep, 1) * 100, 1),
        "lrt_stat":    round(lrt_stat, 2),
        "lrt_p":       "<0.001" if lrt_p < 0.001 else f"{lrt_p:.4f}",
        "c_index":     round(c_index, 3),
        "pw_lr_stat":  round(pw_stat, 2),
        "pw_lr_p":     "<0.001" if pw_p < 0.001 else f"{pw_p:.4f}",
        "g3_lr_stat":  round(g3_stat, 2),
        "g3_lr_p":     "<0.001" if g3_p < 0.001 else f"{g3_p:.4f}",
        "aic_winner":  best_aic[0].title(),
        "aft_aic":     {n: m["aic"] for n, m in aft_models.items()},
        "aft_bic":     {n: m["bic"] for n, m in aft_models.items()},
        "hr":          [round(float(x), 3) for x in np.exp(cox_result.params)],
        "hr_lo":       [round(float(x), 3) for x in np.exp(cox_result.conf_int()[:, 0])],
        "hr_hi":       [round(float(x), 3) for x in np.exp(cox_result.conf_int()[:, 1])],
        "coef_names":  list(edf.columns[edf.columns.str.startswith("z_") | edf.columns.isin(["regime_Mid","regime_High"])]),
        "coefs":       [round(float(x), 4) for x in cox_result.params],
        "coef_se":     [round(float(x), 4) for x in cox_result.bse],
        "coef_pval":   [round(float(x), 4) for x in cox_result.pvalues],
    }
    from survival.config import COX_LABELS
    meta["coef_names"] = COX_LABELS

    return {
        "cox": cox_result, "bch": bch, "z_params": z_params,
        "aft": aft_models, "meta": meta,
        "asset": asset_ticker, "risk": risk_ticker,
    }


def refresh_loop():
    global models

    with lock:
        at = state["config"]["asset"]
        rt = state["config"]["risk"]

    fitted = full_fit(at, rt)
    models.update(fitted)

    while True:
        if refit_event.is_set():
            refit_event.clear()
            with lock:
                at = state["config"]["asset"]
                rt = state["config"]["risk"]
            try:
                fitted = full_fit(at, rt)
                models.update(fitted)
            except Exception:
                err = traceback.format_exc()
                with lock:
                    state["error"] = err
                print(f"  [REFIT ERROR] {err}")

        try:
            sig = score_live(
                models["asset"], models["risk"],
                models["cox"],   models["bch"],
                models["z_params"], models["aft"],
            )
            with lock:
                state["signal"]      = sig
                state["last_update"] = sig["ts"]
                state["status"]      = "live"
                state["model"]       = models["meta"]
                state["error"]       = None
                state["history"].append({
                    "ts":         sig["ts"],
                    "risk":       sig["risk_price"],
                    "rvol":       sig["rvol_pct"],
                    "hr":         sig["rel_hazard"],
                    "regime":     sig["regime"],
                    "risk_level": sig["risk_level"],
                    "asset":      sig["asset_price"],
                })
                if len(state["history"]) > HISTORY_CAP:
                    state["history"] = state["history"][-HISTORY_CAP:]
            print(
                f"  [{sig['ts'][:19]}]  "
                f"{models['asset']}={sig['asset_price']}  "
                f"{models['risk']}={sig['risk_price']}  "
                f"Regime={sig['regime']}  HR={sig['rel_hazard']:.3f}  "
                f"Risk={sig['risk_level']}"
            )
        except Exception:
            err = traceback.format_exc()
            with lock:
                state["status"] = "error"
                state["error"]  = err
            print(f"  [SCORE ERROR] {err}")

        for _ in range(REFRESH_S):
            if refit_event.is_set():
                break
            time.sleep(1)
