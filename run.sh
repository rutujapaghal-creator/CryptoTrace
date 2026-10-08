#!/bin/bash
# ==============================================================================
# PROJECT VED — Crypto Fraud Attribution & Money Flow Tracker
# Standalone Startup Script for Linux / macOS
# ==============================================================================

cd -- "$(dirname "$0")" || exit 1

export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
export PYTHONPATH=".:$PYTHONPATH"

HOST="127.0.0.1"

# 1. Locate Python 3
PY_CMD=""
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null && python -c "import sys; exit(0 if sys.version_info[0] >= 3 else 1)" 2>/dev/null; then
    PY_CMD="python"
fi

if [ -z "$PY_CMD" ]; then
    echo "[-] Error: Python 3 was not found in PATH."
    exit 1
fi

echo "================================================================================"
echo "  PROJECT VED — Crypto Fraud Attribution & Money Flow Tracker                   "
echo "  Python runtime: $("$PY_CMD" --version)                                        "
echo "================================================================================"

# 2. Check dependencies
if ! "$PY_CMD" -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "[+] Installing dependencies (fastapi, uvicorn)..."
    "$PY_CMD" -m pip install fastapi uvicorn || "$PY_CMD" -m pip install --user fastapi uvicorn || true
fi

# 3. Seed database
echo "[+] Checking forensic database & transaction data..."
"$PY_CMD" -c "from ved.database.seed_data import seed_database; seed_database()"

# 4. Port configuration
DEFAULT_PORT=${1:-8000}
PORT=$("$PY_CMD" -c "import socket; print(next(p for p in range($DEFAULT_PORT, $DEFAULT_PORT + 20) if socket.socket().connect_ex(('127.0.0.1', p)) != 0))" 2>/dev/null || echo "$DEFAULT_PORT")

echo "[+] Starting server at: http://${HOST}:${PORT}"
echo "[*] Access the web UI at: http://${HOST}:${PORT}"
echo "================================================================================"
echo ""

"$PY_CMD" -m uvicorn ved.app:app --host "${HOST}" --port "${PORT}"
