#!/bin/bash

# Exit immediately on any error
set -e

# Validate required environment variables
REQUIRED_VARS=("DATABASE_HOST" "DATABASE_PORT" "DATABASE_USER" "DATABASE_PASSWORD" "LOG_REGISTRY_DATABASE_NAME" "LOG_REGISTRY_DATABASE_SCHEMA")
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
DB_URL="postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${LOG_REGISTRY_DATABASE_NAME}"

# Generate models
echo "Generating models for schema '${LOG_REGISTRY_DATABASE_SCHEMA}'..."
sqlacodegen "$DB_URL" --schema "$LOG_REGISTRY_DATABASE_SCHEMA" --outfile "$OUTPUT_FILE"
echo "Models written to: $OUTPUT_FILE"
