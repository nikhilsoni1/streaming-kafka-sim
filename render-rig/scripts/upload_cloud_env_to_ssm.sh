#!/bin/bash
# Upload all key-value pairs from cloud.env to SSM under /render_rig2/

export AWS_PAGER=""

ENV_FILE="cloud.env"

while read -r line; do
  # Skip comments and blank lines
  [[ -z "$line" || "$line" == \#* ]] && continue

  key=$(echo "$line" | cut -d '=' -f 1)
  value=$(echo "$line" | cut -d '=' -f 2-)

  echo "Uploading /render_rig2/$key"
  aws ssm put-parameter \
    --name "/render_rig2/$key" \
    --value "$value" \
    --type "String" \
    --overwrite
done < "$ENV_FILE"
