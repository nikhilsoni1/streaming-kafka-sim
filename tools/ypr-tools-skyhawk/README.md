# ypr-skyhawk

Skyhawk: Lightweight Tactical AWS CLI for EC2, RDS, EMR, and Security Operations.

## Install

```bash
pip install .
```

## Usage

```bash
# EC2
skyhawk ec2 stop-instance --instance-id i-xxxxx [--wait] [--region us-east-1]
skyhawk ec2 start-instance --instance-id i-xxxxx [--wait] [--region us-east-1]
skyhawk ec2 update-ip --instance-id i-xxxxx --new-ip 1.2.3.4 [--region us-east-1]
skyhawk ec2 list-instances [--state running|stopped] [--output table|json] [--region us-east-1] [--save-path ./output.csv]

# RDS
skyhawk rds start-instance --db-id dbxxxxx [--wait] [--region us-east-1]
skyhawk rds stop-instance --db-id dbxxxxx [--wait] [--region us-east-1]
skyhawk rds list-instances [--state available|stopped] [--output table|json] [--region us-east-1] [--save-path ./rds_output.csv]

# EMR
skyhawk emr list-configs [--region us-east-1]

# Security
skyhawk security list-rules [--region us-east-1]
```

## Options

- `--wait`: Wait until EC2 or RDS instance reaches the desired state (start/stop). Timeout enforced.
- `--output`: Choose output format (`table` or `json`). Default is `table`.
- `--save-path`: Save output to a specified path (CSV if table, JSON if json).
- `--state`: Filter EC2 or RDS instances by status (`running`, `stopped`, `available`, etc.).
- `--region`: Specify AWS region. **Default is `us-east-1`.**

## Examples

```bash
# EC2 examples
skyhawk ec2 stop-instance --instance-id i-xxxxx --wait
skyhawk ec2 list-instances --output json --save-path ./ec2_instances.json
skyhawk ec2 list-instances --state running --output table --save-path ./running_instances.csv

# RDS examples
skyhawk rds start-instance --db-id mydb --wait
skyhawk rds list-instances --output table --save-path ./rds_instances.csv
skyhawk rds list-instances --state available --output json --save-path ./available_rds_instances.json

# EMR examples
skyhawk emr list-configs

# Security examples
skyhawk security list-rules
```

## Prompt

[Latest-04/26/25](https://chatgpt.com/c/680d35b9-bba4-8010-9a5e-8b182e325635)

