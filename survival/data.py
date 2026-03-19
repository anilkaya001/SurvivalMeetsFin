import numpy as np
import pandas as pd
import yfinance as yf
from .config import HIST_START, VOL_WIN, MOM_WIN, RISK_LOW, RISK_HIGH


def load_history(asset_ticker: str, risk_ticker: str) -> pd.DataFrame:
    asset = yf.download(asset_ticker, start=HIST_START, auto_adjust=True, progress=False)["Close"].squeeze()
    risk  = yf.download(risk_ticker,  start=HIST_START, auto_adjust=True, progress=False)["Close"].squeeze()
    df = pd.DataFrame({"asset": asset, "risk": risk}).dropna().sort_index()
    df["ret"]        = np.log(df["asset"] / df["asset"].shift(1))
    df["rvol"]       = df["ret"].rolling(VOL_WIN).std() * np.sqrt(252)
    df["vol_spread"] = _vol_spread(df["risk"], df["rvol"])
    df["momentum"]   = df["ret"].rolling(MOM_WIN).sum().shift(1)
    df["risk_lag1"]  = df["risk"].shift(1)
    df["risk_chg5"]  = df["risk"].pct_change(5).shift(1)
    df["log_risk"]   = np.log(df["risk_lag1"].clip(lower=1e-6))
    df["regime"]     = df["risk_lag1"].apply(_classify_regime)
    return df.dropna()


def _vol_spread(risk: pd.Series, rvol: pd.Series) -> pd.Series:
    return risk - rvol * 100.0 if risk.mean() > 5.0 else risk * 100.0 - rvol * 100.0


def _classify_regime(v: float) -> str:
    return "Low" if v < RISK_LOW else ("Mid" if v <= RISK_HIGH else "High")
