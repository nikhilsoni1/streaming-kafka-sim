echo "Syncing EMR scripts..."
aws s3 rm s3://flight-emr/scripts/ --recursive
aws s3 sync orchestration/emr_jobs s3://flight-emr/scripts/ --delete