from aws_repository.services.common_service import create_boto3_client

def list_emr_configurations(region: str = "us-west-2"):
    emr = create_boto3_client('emr', region)
    response = emr.list_clusters()
    return response.get('Clusters', [])