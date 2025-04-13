#!/bin/bash

# Exit on any error
set -e

# Validate schema argument
SCHEMA_NAME="$1"
if [ -z "$SCHEMA_NAME" ]; then
  echo "Please provide a schema name."
  echo "Usage: ./scripts/generate-models.sh <schema-name>"
  exit 1
fi

# Validate required environment variables
REQUIRED_VARS=("DATABASE_HOST" "DATABASE_PORT" "DATABASE_USER" "DATABASE_PASSWORD" "DATABASE_NAME")
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "Environment variable '$var' is not set."
    exit 1
  fi
done

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${REPO_ROOT}/db/models"
OUTPUT_FILE="${OUTPUT_DIR}/${SCHEMA_NAME}.py"
INIT_FILE="${OUTPUT_DIR}/__init__.py"

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"

# Construct SQLAlchemy DB URL
DB_URL="postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"

# Generate models
echo "Generating models for schema '$SCHEMA_NAME'..."
sqlacodegen "$DB_URL" --schema "$SCHEMA_NAME" --outfile "$OUTPUT_FILE"
echo "Models written to: $OUTPUT_FILE"
