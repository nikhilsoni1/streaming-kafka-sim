#!/bin/bash
sudo python3 -m pip install boto3 sqlalchemy psycopg2-binary tqdm
aws s3 cp s3://flight-emr/scripts/db-0.1.0.tar.gz .
sudo python3 -m pip install db-0.1.0.tar.gz
