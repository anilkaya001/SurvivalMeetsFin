#!/usr/bin/env python3
"""
SurvivalMeetsFin — entry point.
Educational research tool: survival analysis applied to market drawdowns.
NOT financial advice. See DISCLAIMER.md.
"""
import warnings
warnings.filterwarnings("ignore")

from server.app import create_app
from survival.config import PORT

if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("  SurvivalMeetsFin — Educational Research Tool")
    print("  NOT financial advice. See DISCLAIMER.md.")
    print("=" * 60)
    print(f"  Dashboard  ->  http://localhost:{PORT}")
    print(f"  API        ->  http://localhost:{PORT}/api/signal")
    print(f"  SSE        ->  http://localhost:{PORT}/api/stream")
    print("=" * 60)
    app.run(host="0.0.0.0", port=PORT, threaded=True, use_reloader=False)
