# ypr-skyhawk

Skyhawk: Lightweight Tactical AWS CLI for EC2, RDS, EMR, and Security Operations.

## Install

```bash
pip install .
```

## Usage

```bash
skyhawk ec2 stop-instance --instance-id i-xxxxx
skyhawk rds start-instance --db-id dbxxxxx
skyhawk emr list-configs
skyhawk security list-rules
```