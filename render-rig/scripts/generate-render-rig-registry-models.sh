#!/bin/bash

# Exit immediately on any error
set -e

# RENDER_RIG_DB_NAME=render-rig
# RENDER_RIG_DB_USER=moffett_blvd
# RENDER_RIG_DB_PASS=plenty-9626-of-401-logs-878
# RENDER_RIG_DB_HOST=elephant01.cizii2a86p9h.us-east-1.rds.amazonaws.com
# RENDER_RIG_DB_PORT=5432

# Validate required environment variables
REQUIRED_VARS=("RENDER_RIG_DB_HOST" "RENDER_RIG_DB_PORT" "RENDER_RIG_DB_USER" "RENDER_RIG_DB_PASS" "RENDER_RIG_DB_NAME")
RENDER_RIG_DB_SCMA="registry"
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "Environment variable '$var' is not set."
    exit 1
  fi
done

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${REPO_ROOT}/render_rig/data_access/database/models"
OUTPUT_FILE="${OUTPUT_DIR}/render_rig_registry_model.py"
INIT_FILE="${OUTPUT_DIR}/__init__.py"

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Construct SQLAlchemy DB URL
DB_URL="postgresql://${RENDER_RIG_DB_USER}:${RENDER_RIG_DB_PASS}@${RENDER_RIG_DB_HOST}:${RENDER_RIG_DB_PORT}/${RENDER_RIG_DB_NAME}"

# Generate models
echo "Generating models for database \"${RENDER_RIG_DB_NAME}\".\"${RENDER_RIG_DB_SCMA}\"..."
sqlacodegen "$DB_URL" --schema "$RENDER_RIG_DB_SCMA" --outfile "$OUTPUT_FILE"
echo "Models written to: $OUTPUT_FILE"
