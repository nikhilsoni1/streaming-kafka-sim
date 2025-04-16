#!/bin/bash
sudo python3 -m pip install boto3 sqlalchemy psycopg2-binary tqdm requests
aws s3 cp s3://flight-emr/jobs/download_px4_logs/libraries/db-0.1.0.tar.gz .
sudo python3 -m pip install db-0.1.0.tar.gz
