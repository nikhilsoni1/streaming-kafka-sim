#!/bin/bash

# Usage: source ./set_env.sh [path_to_env_file]
# Loads environment variables from a file into the current shell.

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Environment file not found: $ENV_FILE"
    return 1 2>/dev/null || exit 1
fi

echo "Loading environment variables from $ENV_FILE"

while IFS='=' read -r key value; do
    # Skip comments and empty lines
    if [[ "$key" =~ ^#.*$ ]] || [[ -z "$key" ]]; then
        continue
    fi

    # Trim whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    export "$key=$value"
    echo "Set: $key=$value"
done < "$ENV_FILE"

echo "Environment variables successfully set."
