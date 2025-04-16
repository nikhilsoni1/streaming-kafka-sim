#!/bin/bash

S3_BUCKET="s3://flight-mwaa"
DAGS_PATH="dags"

echo "Uploading DAGs..."
aws s3 sync $DAGS_PATH $S3_BUCKET/dags/ --delete

echo "Uploading requirements.txt..."
aws s3 cp ./requirements.txt $S3_BUCKET/requirements.txt --delete

echo "Deployment complete!"

# aws s3 cp requirements.txt s3://flight-mwaa/requirements.txt    