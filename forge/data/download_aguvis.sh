#!/bin/bash
# This script downloads the full, raw AGUVIS datasets from the Hugging Face Hub.
# It should be run ON THE REMOTE (Vast.ai) MACHINE.
# Requires git and git-lfs to be installed.

set -e

# --- Configuration ---
RAW_DATA_DIR="./raw" # Download into a 'raw' subdirectory
STAGE1_REPO="https://huggingface.co/datasets/xlangai/aguvis-stage1"
STAGE2_REPO="https://huggingface.co/datasets/xlangai/aguvis-stage2"

# --- Main Logic ---
echo "🔥 Starting FULL AGUVIS dataset download..."
echo "Target directory: $RAW_DATA_DIR"

mkdir -p "$RAW_DATA_DIR"
cd "$RAW_DATA_DIR"

echo "--------------------------------------------------"
echo "Downloading Stage 1: Grounding Dataset..."
if [ -d "aguvis-stage1" ]; then
    echo "Stage 1 directory already exists. Skipping."
else
    GIT_LFS_SKIP_SMUDGE=1 git clone "$STAGE1_REPO"
    cd aguvis-stage1 && git lfs pull && cd ..
    echo "✅ Stage 1 download complete."
fi

echo "--------------------------------------------------"
echo "Downloading Stage 2: Reasoning Dataset..."
if [ -d "aguvis-stage2" ]; then
    echo "Stage 2 directory already exists. Skipping."
else
    GIT_LFS_SKIP_SMUDGE=1 git clone "$STAGE2_REPO"
    cd aguvis-stage2 && git lfs pull && cd ..
    echo "✅ Stage 2 download complete."
fi

echo "✅ All raw materials are now on the remote machine."
