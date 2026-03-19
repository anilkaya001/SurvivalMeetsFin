PORT          = 5050
REFRESH_S     = 60
HIST_START    = "2005-01-01"
DD_THR        = -0.05
VOL_WIN       = 21
MOM_WIN       = 20
RISK_LOW      = 15
RISK_HIGH     = 25
MIN_LIVE_ROWS = 30
HISTORY_CAP   = 120

DEFAULT_ASSET = "QQQ"
DEFAULT_RISK  = "^VIX"

COX_LABELS = [
    "z_log_risk",
    "z_risk_chg5",
    "z_asset_vol",
    "z_vol_spread",
    "z_momentum",
    "regime_Mid",
    "regime_High",
]

AFT_DISTRIBUTIONS = ("weibull", "lognormal", "loglogistic")

HORIZONS = [7, 14, 30, 60, 90, 180]

HR_THRESHOLDS = [
    (3.0, "CRITICAL", "#ef4444"),
    (2.0, "HIGH",     "#f97316"),
    (1.2, "ELEVATED", "#eab308"),
    (0.8, "MODERATE", "#22d3ee"),
    (0.0, "LOW",      "#34d399"),
]
