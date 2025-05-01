#!/bin/bash

# Exit immediately on any error
set -e

# Validate required environment variables
REQUIRED_VARS=("LOG_REGISTRY_DB_HOST" "LOG_REGISTRY_DB_PORT" "LOG_REGISTRY_DB_USER" "LOG_REGISTRY_DB_PASS" "LOG_REGISTRY_DB_NAME")
LOG_REGISTRY_DB_SCMA="registry"
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
OUTPUT_FILE="${OUTPUT_DIR}/px4_registry_model.py"
INIT_FILE="${OUTPUT_DIR}/__init__.py"

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Construct SQLAlchemy DB URL
DB_URL="postgresql://${LOG_REGISTRY_DB_USER}:${LOG_REGISTRY_DB_PASS}@${LOG_REGISTRY_DB_HOST}:${LOG_REGISTRY_DB_PORT}/${LOG_REGISTRY_DB_NAME}"

# Generate models
echo "Generating models for schema '${LOG_REGISTRY_DB_SCMA}'..."
sqlacodegen "$DB_URL" --schema "$LOG_REGISTRY_DB_SCMA" --outfile "$OUTPUT_FILE"
echo "Models written to: $OUTPUT_FILE"
