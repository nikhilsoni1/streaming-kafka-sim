#!/bin/bash
# This script updates an Amazon MWAA (Managed Workflows for Apache Airflow) environment
# with a new requirements file stored in an S3 bucket.
# Variables
ENV_NAME="showrunner-airflow01"
REQUIREMENTS_FILE="requirements.txt"
S3_BUCKET_ARN="arn:aws:s3:::showrunner-airflow01"

# Update the MWAA environment with the new requirements file
aws mwaa update-environment \
    --name "$ENV_NAME" \
    --requirements-s3-path "$REQUIREMENTS_FILE" \
    --source-bucket-arn "$S3_BUCKET_ARN"

echo "MWAA environment '$ENV_NAME' updated with requirements file '$REQUIREMENTS_FILE' in bucket '$S3_BUCKET_ARN'."