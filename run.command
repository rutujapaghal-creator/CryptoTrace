#!/bin/bash
# ==============================================================================
# PROJECT VED — Crypto Fraud Attribution & Money Flow Tracker
# macOS Finder Single-Click Launcher (.command)
# ==============================================================================

# Ensure working directory is the folder where this script is located
cd -- "$(dirname "$0")" || exit 1

# Add standard macOS Python and Homebrew binary paths to PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:$HOME/.local/bin:$PATH"
export PYTHONPATH=".:$PYTHONPATH"

clear
echo "================================================================================"
echo "  PROJECT VED — Crypto Fraud Attribution & Money Flow Tracker                   "
echo "  macOS Single-Click Standalone Launcher                                        "
echo "================================================================================"
echo ""

# 1. Locate Python 3
PY_CMD=""
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null && python -c "import sys; exit(0 if sys.version_info[0] >= 3 else 1)" 2>/dev/null; then
    PY_CMD="python"
fi

if [ -z "$PY_CMD" ]; then
    echo "[-] Error: Python 3 was not found on your system."
    echo "[*] Please install Python 3 (e.g. from https://www.python.org/ or run 'brew install python3')"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[+] Python runtime: $("$PY_CMD" --version)"

# 2. Check and install core dependencies
echo "[+] Checking required packages (fastapi, uvicorn)..."
if ! "$PY_CMD" -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "[*] Installing required packages (fastapi, uvicorn)..."
    "$PY_CMD" -m pip install fastapi uvicorn || "$PY_CMD" -m pip install --user fastapi uvicorn || true
fi

# 3. Initialize & seed database if needed
echo "[+] Initializing forensic database and multi-chain ledger data..."
"$PY_CMD" -c "from ved.database.seed_data import seed_database; seed_database()"

# 4. Determine an available port (starts at 8000, checks 8001, 8002, etc.)
HOST="127.0.0.1"
PORT=$("$PY_CMD" -c "import socket; print(next(p for p in range(8000, 8030) if socket.socket().connect_ex(('127.0.0.1', p)) != 0))" 2>/dev/null || echo 8000)

echo "[+] Bound to local port: ${PORT}"

# 5. Open browser once server is responsive (background poll)
(
    for i in {1..25}; do
        if curl -s "http://${HOST}:${PORT}" >/dev/null 2>&1; then
            break
        fi
        sleep 0.4
    done
    open "http://${HOST}:${PORT}"
) &

# 6. Start Uvicorn Server
echo "[+] Starting CryptoTracker server on http://${HOST}:${PORT}"
echo "[*] Press CTRL+C in this Terminal window to stop the server."
echo "================================================================================"
echo ""

"$PY_CMD" -m uvicorn ved.app:app --host "${HOST}" --port "${PORT}"
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -ne 0 ]; then
    echo "[-] Server exited with status code $EXIT_CODE."
else
    echo "[*] Server stopped cleanly."
fi
echo ""
read -p "Press Enter to close this Terminal window..."
