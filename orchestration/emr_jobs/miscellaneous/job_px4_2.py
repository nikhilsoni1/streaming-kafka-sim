import boto3
from pprint import pprint
import logging
from botocore.exceptions import ClientError
from uuid import uuid4

logger = logging.getLogger(__name__)


def run_job_flow(
    name,
    log_uri,
    applications,
    job_flow_role,
    service_role,
    bootstrap_actions,
    instances,
    steps,
    emr_client,
):
    """
    Runs a job flow with the specified steps. A job flow creates a cluster of
    instances and adds steps to be run on the cluster. Steps added to the cluster
    are run as soon as the cluster is ready.

    This example uses the "emr-5.30.1" release. A list of recent releases can be
    found here:
        https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-release-components.html.

    :param name: The name of the cluster.
    :param log_uri: The URI where logs are stored. This can be an Amazon S3 bucket URL,
                    such as "s3://my-log-bucket".
    :param keep_alive: When True, the cluster is put into a Waiting state after all
                       steps are run. When False, the cluster terminates itself when
                       the step queue is empty.
    :param applications: The applications to install on each instance in the cluster,
                         such as Hive or Spark.
    :param job_flow_role: The IAM role assumed by the cluster.
    :param service_role: The IAM role assumed by the service.
    :param security_groups: The security groups to assign to the cluster instances.
                            Amazon EMR adds all needed rules to these groups, so
                            they can be empty if you require only the default rules.
    :param steps: The job flow steps to add to the cluster. These are run in order
                  when the cluster is ready.
    :param emr_client: The Boto3 EMR client object.
    :return: The ID of the newly created cluster.
    """
    try:
        response = emr_client.run_job_flow(
            Name=name,
            LogUri=log_uri,
            ReleaseLabel="emr-7.8.0",
            Instances=instances,
            Steps=steps,
            BootstrapActions=bootstrap_actions,
            Applications=applications,
            Configurations=[],
            VisibleToAllUsers=True,
            JobFlowRole=job_flow_role,
            ServiceRole=service_role,
            Tags=[
                {"Key": "for-use-with-amazon-emr-managed-policies", "Value": "true"},
                {"Key": "Project", "Value": "FLIGHT"},
            ],
            ScaleDownBehavior="TERMINATE_AT_TASK_COMPLETION",
            StepConcurrencyLevel=1,
        )
        cluster_id = response["JobFlowId"]
        logger.info("Created cluster %s.", cluster_id)
    except ClientError:
        logger.exception("Couldn't create cluster.")
        raise
    else:
        return cluster_id


debug = True
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/emr/client/run_job_flow.html

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    name = f"FLIGHT-EMR-{uuid4()}"
    log_uri = "s3://flight-emr/logs/"
    keep_alive = True
    applications = [
        {"Name": "Hadoop"},
        {"Name": "Spark"},
    ]
    job_flow_role = "AmazonEMR-InstanceProfile-20250406T215321"
    service_role = "AmazonEMR-ServiceRole-20250406T215337"
    service_role = "arn:aws:iam::183295432811:role/service-role/AmazonEMR-ServiceRole-20250406T215337"
    security_groups = {
        "manager": "sg-0fce9a7b34eca8bed",
        "worker": "sg-0246ed716d38c336d",
    }
    bootstrap_actions = [
        {
            "Name": "install-deps",
            "ScriptBootstrapAction": {
                "Path": "s3://flight-emr/scripts/install-dependencies.sh"
            },
        }
    ]
    steps = [
        {
            "Name": f"download-px4-log-{uuid4().hex}",
            "ActionOnFailure": "CANCEL_AND_WAIT",
            "HadoopJarStep": {
                "Properties": [],
                "Jar": "command-runner.jar",
                "Args": [
                    "spark-submit",
                    "--deploy-mode", "cluster",
                    "s3://flight-emr/scripts/download_px4_logs.py",
                ],
            },
        },
    ]
    instances = {
        "InstanceGroups": [
            {
                "Name": "Task - 1",
                "Market": "SPOT",
                "InstanceRole": "TASK",
                "InstanceType": "m4.large",
                "InstanceCount": 2,
                "Configurations": [],
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "VolumeType": "gp2",
                                "SizeInGB": 32,
                            },
                            "VolumesPerInstance": 1,
                        },
                    ],
                    "EbsOptimized": True,
                },
            },
            {
                "Name": "Core",
                "Market": "SPOT",
                "InstanceRole": "CORE",
                "InstanceType": "m4.large",
                "InstanceCount": 1,
                "Configurations": [],
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "VolumeType": "gp2",
                                "SizeInGB": 32,
                            },
                            "VolumesPerInstance": 1,
                        },
                    ],
                    "EbsOptimized": True,
                },
            },
            {
                "Name": "Primary",
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": "m4.large",
                "InstanceCount": 1,
                "Configurations": [],
                "EbsConfiguration": {
                    "EbsBlockDeviceConfigs": [
                        {
                            "VolumeSpecification": {
                                "VolumeType": "gp2",
                                "SizeInGB": 32,
                            },
                            "VolumesPerInstance": 1,
                        },
                    ],
                    "EbsOptimized": True,
                },
            },
        ],
        "KeepJobFlowAliveWhenNoSteps": keep_alive,
        "Ec2SubnetId": "subnet-015c98ab8b3a7e1e5",
        "EmrManagedMasterSecurityGroup": security_groups["manager"],
        "EmrManagedSlaveSecurityGroup": security_groups["worker"],
        "AdditionalMasterSecurityGroups": [],
        "AdditionalSlaveSecurityGroups": [],
    }
    emr_client = boto3.client("emr", region_name="us-east-1")
    cluster_id = run_job_flow(
        name=name,
        log_uri=log_uri,
        bootstrap_actions=bootstrap_actions,
        applications=applications,
        job_flow_role=job_flow_role,
        service_role=service_role,
        instances=instances,
        steps=steps,
        emr_client=emr_client,
    )
    pprint(cluster_id)
