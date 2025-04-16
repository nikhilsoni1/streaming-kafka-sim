aws s3 cp s3://flight-px4-logs/ec2-info/ ./ec2-info/ --recursive --exclude "*" --include "*.json" --include "*.txt"
