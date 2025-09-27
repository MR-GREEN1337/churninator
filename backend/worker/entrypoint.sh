#!/bin/bash
set -e

echo "--- Churninator Worker Entrypoint ---"

echo "[1/2] Starting virtual display (Xvfb) on display :99..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
sleep 2

echo "[2/2] Launching Dramatiq worker..."
# Use `uv run` to execute the command within the virtual environment
exec uv run dramatiq -p 4 -t 4 worker.broker worker.tasks
