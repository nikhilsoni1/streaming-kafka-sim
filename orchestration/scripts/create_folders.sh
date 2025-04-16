#!/bin/bash

# Variables
BUCKET_NAME="flight-mwaa"   # Replace with your bucket name
FOLDER_PATHS=("dags/")  # Add as many folder paths as needed

# Loop through each folder path
for FOLDER in "${FOLDER_PATHS[@]}"; do
    echo "Checking: s3://$BUCKET_NAME/$FOLDER"

    # Check if folder (prefix) exists
    EXISTS=$(aws s3api list-objects-v2 --bucket "$BUCKET_NAME" --prefix "$FOLDER" --max-items 1 --query 'Contents[0].Key' --output text 2>/dev/null)

    if [ "$EXISTS" != "None" ]; then
        echo "❗ Skipping: '$FOLDER' already exists."
        continue
    fi

    # Create folder (zero-byte object with trailing slash)
    aws s3api put-object --bucket "$BUCKET_NAME" --key "$FOLDER"

    if [ $? -eq 0 ]; then
        echo "✅ Created: $FOLDER"
    else
        echo "❌ Failed to create: $FOLDER"
    fi
done
