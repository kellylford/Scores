@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Setting up virtual environment...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt -q
)
echo Starting Sports Scores server at http://localhost:5000
.venv\Scripts\python server.py
