#!/bin/bash
set -e

echo "[entrypoint] Authenticating with AWS CodeArtifact..."
/app/scripts/pip-auth-codeartifact.sh

echo "[entrypoint] Installing Python packages..."
pip install --no-cache-dir -r /app/requirements.txt

echo "[entrypoint] Starting service..."
exec "$@"
