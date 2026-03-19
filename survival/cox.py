"""
Cox Proportional Hazards — Efron partial likelihood,
BFGS optimisation with analytical gradient.
"""

import numpy as np
from scipy.stats import chi2, norm
from scipy.optimize import minimize

from .config import COX_LABELS


class CoxResult:
    def __init__(self, params, bse, pvalues, ci_lo, ci_hi, llf):
        self.params  = params
        self.bse     = bse
        self.pvalues = pvalues
        self._ci_lo  = ci_lo
        self._ci_hi  = ci_hi
        self.llf     = llf

    def conf_int(self, alpha: float = 0.05) -> np.ndarray:
        return np.column_stack([self._ci_lo, self._ci_hi])


def fit_cox(edf):
    X      = edf[COX_LABELS].astype(float).values
    T      = edf["duration"].astype(float).values
    status = edf["event"].astype(int).values
    n, p   = X.shape

    order        = np.argsort(T)
    T_s, d_s, X_s = T[order], status[order], X[order]
    groups       = _build_groups(T_s, d_s, n)
    nll, grad    = _make_efron_objectives(X_s, groups, p)

    res  = minimize(nll, np.zeros(p), jac=grad,
                    method="BFGS", options={"maxiter": 5000, "gtol": 1e-7})
    beta = res.x
    if not res.success or np.any(np.isnan(beta)):
        res  = minimize(nll, np.zeros(p), method="Nelder-Mead",
                        options={"maxiter": 50000, "xatol": 1e-8, "fatol": 1e-8})
        beta = res.x

    se      = _standard_errors(res, beta, grad, p)
    z_vals  = beta / (se + 1e-12)
    pvalues = 2.0 * norm.sf(np.abs(z_vals))
    ci_lo   = beta - 1.96 * se
    ci_hi   = beta + 1.96 * se

    null_nll = nll(np.zeros(p))
    lrt_stat = max(2.0 * (null_nll - res.fun), 0.0)
    lrt_p    = chi2.sf(lrt_stat, df=p)

    bch      = _breslow_baseline(X_s, beta, groups, T_s)
    z_params = _zparams(edf)
    c_index  = _concordance_index(T, status, X @ beta)

    return (CoxResult(beta, se, pvalues, ci_lo, ci_hi, -res.fun),
            lrt_stat, lrt_p, bch, z_params, c_index)


def _build_groups(T_s, d_s, n):
    groups, i = [], 0
    while i < n:
        t_cur, j, ev = T_s[i], i, []
        while j < n and T_s[j] == t_cur:
            if d_s[j] == 1:
                ev.append(j)
            j += 1
        groups.append((i, j, ev))
        i = j
    return groups


def _make_efron_objectives(X_s, groups, p):
    def nll(beta):
        xb     = X_s @ beta
        c      = xb.max()
        exp_xb = np.exp(xb - c)
        rsum   = np.cumsum(exp_xb[::-1])[::-1]
        val    = 0.0
        for start, _, ev_idx in groups:
            dj = len(ev_idx)
            if dj == 0:
                continue
            val -= float(np.sum(xb[ev_idx]))
            rs   = rsum[start]
            es   = float(np.sum(exp_xb[ev_idx]))
            for r in range(dj):
                val += c + np.log(max(rs - (r / dj) * es, 1e-300))
        return val

    def grad(beta):
        xb     = X_s @ beta
        c      = xb.max()
        exp_xb = np.exp(xb - c)
        rsum   = np.cumsum(exp_xb[::-1])[::-1]
        wX     = X_s * exp_xb[:, None]
        wX_rs  = np.cumsum(wX[::-1], axis=0)[::-1]
        g      = np.zeros(p)
        for start, _, ev_idx in groups:
            dj = len(ev_idx)
            if dj == 0:
                continue
            g   -= np.sum(X_s[ev_idx], axis=0)
            rs   = rsum[start]
            es   = float(np.sum(exp_xb[ev_idx]))
            rwX  = wX_rs[start]
            ewX  = np.sum(wX[ev_idx], axis=0)
            for r in range(dj):
                frac  = r / dj
                denom = max(rs - frac * es, 1e-300)
                g    += (rwX - frac * ewX) / denom
        return g

    return nll, grad


def _standard_errors(res, beta, grad, p):
    if hasattr(res, "hess_inv") and res.hess_inv is not None:
        H_inv = np.asarray(res.hess_inv)
        return np.sqrt(np.maximum(np.diag(H_inv), 0.0))
    eps = np.sqrt(np.finfo(float).eps)
    g0  = grad(beta)
    H   = np.zeros((p, p))
    for k in range(p):
        ek = np.zeros(p); ek[k] = eps
        H[:, k] = (grad(beta + ek) - g0) / eps
    H = 0.5 * (H + H.T)
    try:
        return np.sqrt(np.maximum(np.diag(np.linalg.inv(H)), 0.0))
    except np.linalg.LinAlgError:
        return np.full(p, np.nan)


def _breslow_baseline(X_s, beta, groups, T_s):
    xb_f   = np.clip(X_s @ beta, -500, 500)
    exp_f  = np.exp(xb_f)
    rsum_f = np.cumsum(exp_f[::-1])[::-1]
    b_times, b_H0, cum_h = [], [], 0.0
    for start, _, ev_idx in groups:
        dj = len(ev_idx)
        if dj > 0:
            rs = rsum_f[start]
            es = float(np.sum(exp_f[ev_idx]))
            for r in range(dj):
                cum_h += 1.0 / max(rs - (r / dj) * es, 1e-300)
        b_times.append(T_s[start])
        b_H0.append(cum_h)
    return [(np.array(b_times), np.array(b_H0))]


def _zparams(edf):
    zp = {}
    for col in ("log_risk", "risk_chg5", "rvol", "vol_spread", "momentum"):
        zp[f"{col}_mean"] = float(edf[col].mean())
        zp[f"{col}_std"]  = float(edf[col].std())
    return zp


def _concordance_index(T, event, risk_score):
    if np.any(np.isnan(risk_score)):
        return 0.5
    ev_idx = np.where(event == 1)[0]
    conc = disc = tied = 0
    for i in ev_idx:
        rs_j  = risk_score[T > T[i]]
        conc += int(np.sum(risk_score[i] > rs_j))
        disc += int(np.sum(risk_score[i] < rs_j))
        tied += int(np.sum(risk_score[i] == rs_j))
    denom = conc + disc + tied
    return conc / denom if denom > 0 else 0.5
