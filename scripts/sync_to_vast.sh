#!/bin/bash

# --- Configuration ---
REMOTE_USER="root"
REMOTE_HOST="<IP_ADDRESS>"
REMOTE_PORT="<PORT>"

# The remote directory with your results
REMOTE_DIR="/workspace/forge/checkpoints/"
# The local destination
LOCAL_DIR="./forge/checkpoints/"

echo "🔽 Syncing results from the remote machine..."

# Create the local directory if it doesn't exist
mkdir -p "$LOCAL_DIR"

rsync -avz \
  -e "ssh -p $REMOTE_PORT" \
  "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR" \
  "$LOCAL_DIR"

echo "✅ Results sync complete."
