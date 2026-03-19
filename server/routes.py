"""Flask API routes."""

import json
import time

from flask import Blueprint, Response, jsonify, request

from survival.config import DEFAULT_ASSET, DEFAULT_RISK
from .state import state, lock, refit_event

bp = Blueprint("api", __name__)


@bp.route("/api/signal")
def api_signal():
    with lock:
        return jsonify(state)


@bp.route("/api/config", methods=["POST"])
def api_config():
    data  = request.get_json(force=True)
    asset = str(data.get("asset", DEFAULT_ASSET)).upper().strip()[:20]
    risk  = str(data.get("risk",  DEFAULT_RISK)).upper().strip()[:20]
    with lock:
        state["config"]["asset"] = asset
        state["config"]["risk"]  = risk
        state["status"]          = "refitting"
        state["history"]         = []
    refit_event.set()
    return jsonify({"ok": True, "asset": asset, "risk": risk})


@bp.route("/api/stream")
def api_stream():
    def gen():
        seen = None
        while True:
            with lock:
                ts = state.get("last_update")
            if ts != seen:
                seen = ts
                with lock:
                    payload = json.dumps(state)
                yield f"data: {payload}\n\n"
            time.sleep(2)
    return Response(
        gen(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
