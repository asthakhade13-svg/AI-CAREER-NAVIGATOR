@echo off
REM ── AI Career Navigator — Backend Launcher ─────────────────────────────────
REM Uses system Python (not venv) because Windows Application Control policy
REM blocks compiled .pyd DLLs installed inside the project venv directory.
REM System Python 3.14 has all packages installed at the system site-packages level.
REM
REM To run:  double-click this file, or:  cd backend && start.bat

cd /d "%~dp0"
echo Starting AI Career Navigator backend on http://localhost:8000 ...
python app.py
pause
