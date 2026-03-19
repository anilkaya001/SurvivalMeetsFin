import numpy as np
import pandas as pd
from .config import DD_THR


def build_episodes(df: pd.DataFrame) -> pd.DataFrame:
    prices, dates, rows = df["asset"].values, df.index, []
    i = 0
    while i < len(df) - 1:
        pk, sd = prices[i], dates[i]
        cov = {k: df[k].iat[i] for k in
               ["risk_lag1","log_risk","risk_chg5","rvol","vol_spread","momentum","regime"]}
        cov = {"risk": cov.pop("risk_lag1"), **cov}
        event, j = 0, i + 1
        while j < len(df):
            dd = prices[j] / pk - 1.0
            if dd <= DD_THR:  event = 1; break
            if prices[j] > pk: break
            j += 1
        ed  = dates[j] if j < len(df) else dates[-1]
        dur = (ed - sd).days
        if dur > 0:
            rows.append({"start": sd, "duration": dur, "event": event, **cov})
        i = j if j < len(df) else len(df)

    edf = pd.DataFrame(rows).dropna()
    edf = pd.get_dummies(edf, columns=["regime"], drop_first=False)
    for col in ("regime_Low", "regime_Mid", "regime_High"):
        if col not in edf.columns:
            edf[col] = 0

    for raw, z_name in [("log_risk","z_log_risk"),("risk_chg5","z_risk_chg5"),
                         ("rvol","z_asset_vol"),("vol_spread","z_vol_spread"),("momentum","z_momentum")]:
        edf[z_name] = _zscore(edf[raw])
    return edf


def _zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / (s.std() + 1e-12)
