#!/bin/bash
cd "$(dirname "$0")"
if [[ ! -f ".venv/bin/python" ]]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt -q
fi
echo "Starting Sports Scores server at http://localhost:5000"
.venv/bin/python server.py
