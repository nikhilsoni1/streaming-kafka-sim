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
: "${DATABASE_USER:?Missing DATABASE_USER}"
: "${DATABASE_PASSWORD:?Missing DATABASE_PASSWORD}"
: "${DATABASE_HOST:?Missing DATABASE_HOST}"
: "${DATABASE_PORT:?Missing DATABASE_PORT}"
: "${DATABASE_NAME:?Missing DATABASE_NAME}"

# Export for psql
export PGPASSWORD="$DATABASE_PASSWORD"

echo "🔍 Checking connection to $DATABASE_HOST:$DATABASE_PORT/$DATABASE_NAME as $DATABASE_USER..."

# Run a simple query to verify the connection
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "SELECT NOW();"

echo "✅ Connection successful."

# === Drop and recreate public schema ===
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "DROP SCHEMA public CASCADE;"
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "CREATE SCHEMA public;"
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "GRANT ALL ON SCHEMA public TO postgres;"
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c "GRANT ALL ON SCHEMA public TO public;"

# === Drop and recreate px4 database ===
echo "🚨 Dropping database 'px4' if it exists..."
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d postgres -c "DROP DATABASE IF EXISTS px4;"

echo "✅ Creating fresh database 'px4'..."
psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d postgres -c "CREATE DATABASE px4;"

# === Create schemas inside px4 ===
echo "📁 Creating schemas inside 'px4'..."
for schema in dbinfo registry transformed_data; do
  echo "➕ Creating schema: $schema"
  psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d px4 -c "CREATE SCHEMA IF NOT EXISTS $schema;"
done

echo "🎉 Done! Database 'px4' is reset and schemas created."
