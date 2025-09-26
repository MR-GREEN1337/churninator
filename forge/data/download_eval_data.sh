#!/bin/bash
# This script downloads the ScreenSpot benchmark dataset for evaluation.
# Run from the project root: bash forge/data/download_eval_data.sh

set -e

EVAL_DATA_DIR="forge/data/eval_data"
REPO="https://huggingface.co/datasets/HongxinLi/ScreenSpot_v2"

echo "🔥 Downloading ScreenSpot_v2 evaluation dataset..."
echo "Target directory: $EVAL_DATA_DIR"

mkdir -p "$EVAL_DATA_DIR"
cd "$EVAL_DATA_DIR"

if [ -d "ScreenSpot_v2" ]; then
    echo "ScreenSpot_v2 directory already exists. Skipping download."
else
    GIT_LFS_SKIP_SMUDGE=1 git clone "$REPO" ScreenSpot_v2
    cd ScreenSpot_v2
    git lfs pull
    cd ..
    echo "✅ ScreenSpot_v2 download complete."
fi

cd ../../.. # Return to project root
