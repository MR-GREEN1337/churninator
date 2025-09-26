#!/bin/bash
set -e

# This entrypoint script is run from inside the Docker container.
# The project source code is located at /app/src.

echo "--- Churninator Worker Entrypoint ---"

# --- No `pip install -e .` needed ---
# Because we set PYTHONPATH=/app/src, Python can already find all our modules.
# We just need to install Playwright's browsers.

echo "[1/3] Installing Playwright browsers..."
playwright install --with-deps

echo "[2/3] Starting virtual display (Xvfb) on display :99..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
sleep 2

# --- CORRECTED COMMAND ---
# We now call dramatiq and point it to the correct module path inside `src`.
echo "[3/3] Launching Dramatiq worker..."
exec uv run dramatiq -p 4 -t 4 src.worker.tasks
