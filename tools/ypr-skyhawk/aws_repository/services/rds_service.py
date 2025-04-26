from aws_repository.services.common_service import create_boto3_client

def stop_rds_instance(db_id: str, region: str = "us-west-2"):
    rds = create_boto3_client('rds', region)
    rds.stop_db_instance(DBInstanceIdentifier=db_id)

def start_rds_instance(db_id: str, region: str = "us-west-2"):
    rds = create_boto3_client('rds', region)
    rds.start_db_instance(DBInstanceIdentifier=db_id)