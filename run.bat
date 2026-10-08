@echo off
TITLE CryptoTracker - Project VED
COLOR 0B

:: Ensure working directory is always the folder where this batch file is stored
cd /d "%~dp0"

:: Add current folder to PYTHONPATH
set "PYTHONPATH=%~dp0;%PYTHONPATH%"

echo ================================================================================
echo   PROJECT VED - Crypto Fraud Attribution ^& Money Flow Tracker
echo   Windows Standalone Launcher
echo ================================================================================
echo.

:: 1. Detect Python command
set "PY_CMD="
py -3 --version >nul 2>nul && set "PY_CMD=py -3"
if not defined PY_CMD (
    python --version >nul 2>nul && set "PY_CMD=python"
)
if not defined PY_CMD (
    py --version >nul 2>nul && set "PY_CMD=py"
)
if not defined PY_CMD (
    python3 --version >nul 2>nul && set "PY_CMD=python3"
)

if not defined PY_CMD (
    COLOR 0C
    echo [-] Error: Python was not found on your system.
    echo [*] Please install Python 3.9+ from https://www.python.org/
    echo [*] Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [+] Python runtime detected:
%PY_CMD% --version
echo.

:: 2. Check and install core dependencies
echo [+] Checking required packages (fastapi, uvicorn)...
%PY_CMD% -c "import fastapi, uvicorn" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing required packages (fastapi, uvicorn)...
    %PY_CMD% -m pip install fastapi uvicorn
)

:: 3. Initialize & seed database if needed
echo [+] Initializing forensic database and multi-chain ledger data...
%PY_CMD% -c "from ved.database.seed_data import seed_database; seed_database()"

:: 4. Find first available port (starting from 8000)
set "PORT=8000"
for /f "tokens=*" %%p in ('%PY_CMD% -c "import socket; print(next(p for p in range(8000, 8030) if socket.socket().connect_ex(('127.0.0.1', p)) != 0))" 2^>nul') do set "PORT=%%p"

echo [+] Bound to local port: %PORT%

:: 5. Launch browser after 2 second delay (gives uvicorn time to start listening)
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:%PORT%"

:: 6. Start Uvicorn Server
echo [+] Starting CryptoTracker server on http://127.0.0.1:%PORT%
echo [*] Press CTRL+C in this command window to stop the server.
echo ================================================================================
echo.

%PY_CMD% -m uvicorn ved.app:app --host 127.0.0.1 --port %PORT%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [-] Server stopped with error code %ERRORLEVEL%.
)

echo.
pause
