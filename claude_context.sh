#!/bin/bash
#
# Churninator - Context Generation Script v2.0 (Final)
# Gathers all RELEVANT source, configs, and scripts, with robust exclusions.
#

echo "--- Generating complete context for The Churninator ---"

# --- Step 1: Clear previous context ---
echo "[1/5] Clearing old context file..."
> context.txt

# --- Step 2: Append Forge & Backend Source (Python) ---
echo "[2/5] Appending Forge & Backend source files (*.py)..."
find forge backend -type f -name "*.py" \
  -not -path "*/.venv/*" \
  -not -path "*/__pycache__/*" \
  -exec sh -c '
  echo "File: {}" >> context.txt && cat {} >> context.txt && echo -e "\n-e \n-e" >> context.txt
' \;

# --- Step 3: Append Frontend Source (Next.js) ---
echo "[3/5] Appending Frontend source files (*.ts, *.tsx)..."
find web -type f \( -name "*.ts" -o -name "*.tsx" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.next/*" \
  -exec sh -c '
  echo "File: $1" >> context.txt && cat "$1" >> context.txt && echo -e "\n-e \n-e" >> context.txt
' sh {} \;

# --- Step 4: Append Configs & Scripts (YAML & Shell) ---
echo "[4/5] Appending Configs (*.yaml) & Scripts (*.sh)..."
# THE FIX IS HERE: We now exclude .venv, .git, and node_modules from this global find.
find . -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.sh" \) \
  -not -path "./.git/*" \
  -not -path "*/.venv/*" \
  -not -path "*/node_modules/*" \
  -not -path "./forge/data/raw/*" \
  -exec sh -c '
  echo "File: {}" >> context.txt && cat {} >> context.txt && echo -e "\n-e \n-e" >> context.txt
' \;

# --- Step 5: Append Directory Trees & Final Prompt ---
echo "[5/5] Appending directory trees and project prompt..."
{
  echo "--- DIRECTORY TREES ---"
  echo ""
  echo "Forge Tree:"
  tree -I '.venv|__pycache__|data/raw|checkpoints|*.egg-info' forge
  echo ""
  echo "Backend Tree:"
  tree -I '.venv|__pycache__|.pytest_cache' backend
  echo ""
  echo "Frontend Tree (web/):"
  tree -I 'node_modules|.next|out' web
  echo ""
  echo "-----------------------"
  echo ""
} >> context.txt

# Append your startup context at the bottom
cat <<'EOT' >> context.txt
Project Context: The Churninator - Autonomous AI Mystery Shopper for SaaS

Core Concept: An open-source, AI-powered platform designed to autonomously analyze the signup and onboarding experience of any web application. It acts as a "mystery shopper," identifying UX friction points, conversion killers, and usability issues, then presents the findings in a detailed, interactive report.

System Architecture: Multi-Component, Cloud-Native Platform

1. The Forge (forge/):
Role: The "AI Workshop & ML Pipeline."
Function: Contains all scripts for the two-stage AGUVIS fine-tuning methodology (Stage 1: Grounding, Stage 2: Reasoning). It's designed for full-scale training on remote cloud GPUs (like Vast.ai).

2. The Backend (backend/):
Role: The "Mission Control & Production Engine."
Sub-components:
- API / Control Plane (backend/api/): FastAPI server for user requests and job queuing (Redis).
- Agent Worker (backend/worker/): Scalable Celery workers running Playwright in a virtual display (Xvfb).
- Inference Server (backend/inference/): Hosts the fine-tuned Churninator model (e.g., using vLLM), acting as the remote brain for the workers.

3. The Frontend (web/):
Role: The "Observatory & Executive Dashboard."
Function: A Next.js application with a "live view" dashboard (WebSockets for logs, MJPEG for video) to observe agents in real-time.

User Experience & Core Loop:
A user submits a URL and task. The API queues a job. A Worker picks it up, streams its browser view and "thoughts" to the frontend, and generates a final report on all discovered UX issues.
EOT

echo "--- Context generation complete. File 'context.txt' is ready. ---"
