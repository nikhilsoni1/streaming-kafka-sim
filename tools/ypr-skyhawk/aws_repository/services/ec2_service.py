from aws_repository.services.common_service import create_boto3_client

def stop_ec2_instance(instance_id: str, region: str = "us-west-2"):
    ec2 = create_boto3_client('ec2', region)
    ec2.stop_instances(InstanceIds=[instance_id])

def start_ec2_instance(instance_id: str, region: str = "us-west-2"):
    ec2 = create_boto3_client('ec2', region)
    ec2.start_instances(InstanceIds=[instance_id])

def update_instance_ip(instance_id: str, new_ip: str, region: str = "us-west-2"):
    ec2 = create_boto3_client('ec2', region)
    ec2.modify_instance_attribute(InstanceId=instance_id, SourceDestCheck={'Value': False})