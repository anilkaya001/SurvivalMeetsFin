"""Log-rank tests: pairwise (1 df) and 3-group Mantel-Haenszel (2 df)."""

import numpy as np
from scipy.stats import chi2


def pairwise_logrank(edf, g1: str = "regime_Low", g2: str = "regime_High"):
    low  = edf[edf[g1] == 1]
    high = edf[edf[g2] == 1]
    if len(low) < 5 or len(high) < 5:
        return 0.0, 1.0
    all_t = np.sort(np.unique(edf.loc[edf["event"] == 1, "duration"].values))
    O1 = E1 = V = 0.0
    for t in all_t:
        n1 = float((low["duration"]  >= t).sum())
        n2 = float((high["duration"] >= t).sum())
        d1 = float(((low["duration"]  == t) & (low["event"]  == 1)).sum())
        d2 = float(((high["duration"] == t) & (high["event"] == 1)).sum())
        nn = n1 + n2; dd = d1 + d2
        if nn < 2 or dd == 0:
            continue
        O1 += d1
        E1 += dd * n1 / nn
        V  += dd * (nn - dd) * n1 * n2 / (nn * nn * max(nn - 1, 1))
    stat = (O1 - E1) ** 2 / max(V, 1e-12)
    return float(stat), float(chi2.sf(stat, df=1))


def three_group_logrank(edf):
    gcols = ["regime_Low", "regime_Mid", "regime_High"]
    grps  = [edf[edf[c] == 1] for c in gcols]
    if any(len(g) < 3 for g in grps):
        return 0.0, 1.0
    K     = 3
    all_t = np.sort(np.unique(edf.loc[edf["event"] == 1, "duration"].values))
    O = np.zeros(K); E = np.zeros(K); V = np.zeros((K, K))
    for t in all_t:
        n_k = np.array([(g["duration"] >= t).sum() for g in grps], dtype=float)
        d_k = np.array([((g["duration"] == t) & (g["event"] == 1)).sum()
                        for g in grps], dtype=float)
        nn = n_k.sum(); dd = d_k.sum()
        if nn < 2 or dd == 0:
            continue
        O += d_k
        E += dd * n_k / nn
        for a in range(K):
            for b in range(K):
                if a == b:
                    V[a, b] += (dd * (nn - dd) * n_k[a] * (nn - n_k[a])
                                / (nn * nn * max(nn - 1, 1)))
                else:
                    V[a, b] -= (dd * (nn - dd) * n_k[a] * n_k[b]
                                / (nn * nn * max(nn - 1, 1)))
    OE = (O - E)[:-1]
    Vr = V[:-1, :-1]
    try:
        stat = float(OE @ np.linalg.inv(Vr) @ OE)
    except np.linalg.LinAlgError:
        stat = 0.0
    return float(stat), float(chi2.sf(stat, df=K - 1))
