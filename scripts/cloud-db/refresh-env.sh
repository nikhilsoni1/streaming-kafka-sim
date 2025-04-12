#!/bin/bash
set -euo pipefail

# === Validate & load ENV file from argument ===
if [ "$#" -lt 1 ]; then
  echo "❌ Usage: $0 path/to/env-file"
  exit 1
fi

ENV_FILE="$1"

if [ -f "$ENV_FILE" ]; then
  echo "🔄 Loading environment variables from $ENV_FILE"
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "❌ Environment file '$ENV_FILE' not found."
  exit 1
fi

# Required env variables
: "${DB_USER:?Missing DB_USER}"
: "${DB_PASSWORD:?Missing DB_PASSWORD}"
: "${DB_HOST:?Missing DB_HOST}"
: "${DB_PORT:?Missing DB_PORT}"
: "${DB_NAME:?Missing DB_NAME}"

# Export for psql
export PGPASSWORD="$DB_PASSWORD"

echo "🔍 Checking connection to $DB_HOST:$DB_PORT/$DB_NAME as $DB_USER..."

# Run a simple query to verify the connection
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT NOW();"

echo "✅ Connection successful."

# === Drop and recreate px4 database ===
echo "🚨 Dropping database 'px4' if it exists..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS px4;"

echo "✅ Creating fresh database 'px4'..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE px4;"

# === Create schemas inside px4 ===
echo "📁 Creating schemas inside 'px4'..."
for schema in dbinfo registry transformed_data; do
  echo "➕ Creating schema: $schema"
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d px4 -c "CREATE SCHEMA IF NOT EXISTS $schema;"
done

echo "🎉 Done! Database 'px4' is reset and schemas created."
