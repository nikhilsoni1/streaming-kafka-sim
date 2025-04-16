#!/bin/bash
set -euo pipefail

# Get absolute path to the directory this script is in
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="${SCRIPT_DIR}/../../.."  # adjust this as needed

echo "Syncing scripts to S3 for job – download_px4_logs ..."

aws s3 rm s3://flight-emr/jobs/download_px4_logs/scripts/ --recursive

aws s3 cp "${PROJECT_ROOT}/orchestration/emr_jobs/download_px4_logs/main.py" \
          s3://flight-emr/jobs/download_px4_logs/scripts/main.py

aws s3 cp "${PROJECT_ROOT}/orchestration/emr_jobs/download_px4_logs/bootstrap.sh" \
          s3://flight-emr/jobs/download_px4_logs/scripts/bootstrap.sh

echo "Syncing libraries to S3 for job – download_px4_logs ..."

aws s3 rm s3://flight-emr/jobs/download_px4_logs/libraries/ --recursive

aws s3 cp "${PROJECT_ROOT}/orchestration/emr_jobs/download_px4_logs/db-0.1.0.tar.gz" \
          s3://flight-emr/jobs/download_px4_logs/libraries/db-0.1.0.tar.gz
