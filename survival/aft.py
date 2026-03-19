"""Parametric AFT models: Weibull, Log-Normal, Log-Logistic."""

import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize

from .config import COX_LABELS


def fit_aft(edf, dist: str = "weibull"):
    X = np.column_stack([np.ones(len(edf)), edf[COX_LABELS].astype(float).values])
    T = edf["duration"].astype(float).values
    d = edf["event"].astype(int).values
    k, n  = X.shape[1], len(edf)
    p0    = np.zeros(k + 1)
    p0[0] = np.log(max(T.mean(), 1.0))
    res   = minimize(_aft_nll, p0, args=(X, T, d, dist), method="Nelder-Mead",
                     options={"maxiter": 50000, "xatol": 1e-9, "fatol": 1e-9})
    beta  = res.x[:k]
    sigma = np.exp(res.x[k])
    n_par = k + 1
    aic   = 2 * n_par + 2 * res.fun
    bic   = n_par * np.log(n) + 2 * res.fun
    shape = (1.0 / sigma) if dist in ("weibull", "loglogistic") else sigma
    return shape, sigma, beta, aic, bic


def _aft_nll(params, X, T, d, dist: str) -> float:
    k     = X.shape[1]
    beta  = params[:k]
    sigma = np.exp(params[k])
    z     = (np.log(np.maximum(T, 1e-10)) - X @ beta) / sigma

    if dist == "weibull":
        log_f = z - np.exp(z) - params[k]
        log_S = -np.exp(z)
    elif dist == "lognormal":
        log_f = norm.logpdf(z) - params[k]
        log_S = norm.logsf(z)
    elif dist == "loglogistic":
        log_f = z - 2.0 * np.log1p(np.exp(z)) - params[k]
        log_S = -np.log1p(np.exp(z))
    else:
        raise ValueError(f"Unknown distribution: {dist!r}")

    return -float(np.sum(np.where(d == 1, log_f, log_S)))
