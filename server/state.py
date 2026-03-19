"""Shared application state and threading primitives."""

import threading

from survival.config import DEFAULT_ASSET, DEFAULT_RISK

state = {
    "status":      "booting",
    "last_update": None,
    "config":      {"asset": DEFAULT_ASSET, "risk": DEFAULT_RISK},
    "signal":      {},
    "history":     [],
    "model":       {},
    "error":       None,
}

lock         = threading.Lock()
refit_event  = threading.Event()
models: dict = {}
