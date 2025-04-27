from aws_repository.services.common_service import create_boto3_client


def list_security_rules(region: str = "us-west-2"):
    ec2 = create_boto3_client("ec2", region)
    response = ec2.describe_security_groups()
    return response.get("SecurityGroups", [])
