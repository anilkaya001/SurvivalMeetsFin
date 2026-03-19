"""Live covariate construction and model scoring."""

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm

from .config import (
    VOL_WIN, MOM_WIN, RISK_LOW, RISK_HIGH,
    MIN_LIVE_ROWS, HORIZONS, HR_THRESHOLDS,
)


def score_live(asset_ticker, risk_ticker, cox_result, bch, z_params, aft_models):
    df = _fetch_live(asset_ticker, risk_ticker)
    if len(df) < MIN_LIVE_ROWS:
        raise ValueError(
            f"Only {len(df)} rows after feature engineering "
            f"(need >= {MIN_LIVE_ROWS})"
        )
    last      = df.iloc[-1]
    risk_now  = float(last["risk"])
    asset_now = float(last["asset"])
    rvol_now  = float(last["rvol"])
    vs_now    = float(last["vol_spread"])
    mom_now   = float(last["momentum"])
    log_risk  = np.log(max(risk_now, 1e-6))
    risk_chg5 = (float(df["risk"].iloc[-1] / df["risk"].iloc[-6] - 1)
                 if len(df) >= 6 else 0.0)
    regime    = _classify(risk_now)

    x_row  = _build_x(log_risk, risk_chg5, rvol_now, vs_now,
                      mom_now, regime, z_params)
    lp     = float(x_row @ cox_result.params)
    hr     = np.exp(lp)
    cox_sv = {f"d{t}": round(_cox_surv(bch, hr, t) * 100, 1) for t in HORIZONS}
    aft_sv = {
        name: {
            f"d{t}": round(_aft_surv(m["dist"], m["sigma"],
                                     m["beta"], x_row, t) * 100, 1)
            for t in HORIZONS
        }
        for name, m in aft_models.items()
    }
    rl, rc = _risk_label(hr)

    return {
        "ts":           datetime.now(timezone.utc).isoformat(),
        "asset_price":  round(asset_now, 2),
        "risk_price":   round(risk_now, 2),
        "rvol_pct":     round(rvol_now * 100, 2),
        "vol_spread":   round(vs_now, 2),
        "momentum_pct": round(mom_now * 100, 2),
        "risk_chg5":    round(risk_chg5 * 100, 2),
        "regime":       regime,
        "linear_pred":  round(lp, 4),
        "rel_hazard":   round(hr, 4),
        "risk_level":   rl,
        "risk_col":     rc,
        "cox_surv":     cox_sv,
        "aft_surv":     aft_sv,
        "spark":        _sparkline(df),
        "horizons":     HORIZONS,
    }


def _fetch_live(asset_ticker, risk_ticker):
    a  = yf.download(asset_ticker, period="120d",
                     auto_adjust=True, progress=False)["Close"].squeeze()
    r  = yf.download(risk_ticker,  period="120d",
                     auto_adjust=True, progress=False)["Close"].squeeze()
    df = pd.DataFrame({"asset": a, "risk": r}).dropna().sort_index()
    df["ret"]  = np.log(df["asset"] / df["asset"].shift(1))
    df["rvol"] = df["ret"].rolling(VOL_WIN).std() * np.sqrt(252)
    df["vol_spread"] = (df["risk"] - df["rvol"] * 100.0
                        if df["risk"].mean() > 5.0
                        else df["risk"] * 100.0 - df["rvol"] * 100.0)
    df["momentum"] = df["ret"].rolling(MOM_WIN).sum()
    return df.dropna()


def _classify(v: float) -> str:
    return "Low" if v < RISK_LOW else ("Mid" if v <= RISK_HIGH else "High")


def _build_x(log_risk, risk_chg5, rvol, vs, mom, regime, zp):
    def zs(v, k):
        return (v - zp[f"{k}_mean"]) / (zp[f"{k}_std"] + 1e-12)
    return np.array([
        zs(log_risk,  "log_risk"),
        zs(risk_chg5, "risk_chg5"),
        zs(rvol,      "rvol"),
        zs(vs,        "vol_spread"),
        zs(mom,       "momentum"),
        1 if regime == "Mid"  else 0,
        1 if regime == "High" else 0,
    ])


def _cox_surv(bch, hr, t):
    bt, H0 = bch[0][0], bch[0][1]
    idx = np.searchsorted(bt, t, side="right") - 1
    h0  = H0[idx] if 0 <= idx < len(H0) else H0[-1]
    return float(np.exp(-h0 * hr))


def _aft_surv(dist, sigma, beta, x_row, t):
    xr = np.concatenate([[1.0], x_row])
    mu = float(xr @ beta)
    z  = (np.log(max(t, 1e-10)) - mu) / sigma
    if dist == "weibull":
        return float(np.exp(-np.exp(z)))
    if dist == "lognormal":
        return float(norm.sf(z))
    if dist == "loglogistic":
        return float(1.0 / (1.0 + np.exp(z)))
    return 0.5


def _risk_label(hr):
    for threshold, label, color in HR_THRESHOLDS:
        if hr > threshold:
            return label, color
    return "LOW", "#34d399"


def _sparkline(df):
    return [
        {"t": str(d)[:10], "risk": round(float(r), 2),
         "asset": round(float(a), 2)}
        for d, r, a in zip(df.index[-60:],
                           df["risk"].values[-60:],
                           df["asset"].values[-60:])
    ]
