import argparse
import json
import logging
import os
import sys
import time
from pprint import pprint
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
import yaml

logger = logging.getLogger(__name__)

def status_poller(intro, done_status, func):
    """
    Polls a function for status, sleeping for 10 seconds between each query,
    until the specified status is returned.

    :param intro: An introductory sentence that informs the reader what we're
                  waiting for.
    :param done_status: The status we're waiting for. This function polls the status
                        function until it returns the specified status.
    :param func: The function to poll for status. This function must eventually
                 return the expected done_status or polling will continue indefinitely.
    """
    logger.setLevel(logging.WARNING)
    status = None
    print(intro)
    print("Current status: ", end="")
    while status != done_status:
        prev_status = status
        status = func()
        if prev_status == status:
            print(".", end="")
        else:
            print(status, end="")
        sys.stdout.flush()
        time.sleep(10)
    print()
    logger.setLevel(logging.INFO)

def describe_cluster(cluster_id, emr_client):
    """
    Gets detailed information about a cluster.

    :param cluster_id: The ID of the cluster to describe.
    :param emr_client: The Boto3 EMR client object.
    :return: The retrieved cluster information.
    """
    try:
        response = emr_client.describe_cluster(ClusterId=cluster_id)
        cluster = response["Cluster"]
        logger.info("Got data for cluster %s.", cluster["Name"])
    except ClientError:
        logger.exception("Couldn't get data for cluster %s.", cluster_id)
        raise
    else:
        return cluster

def list_steps(cluster_id, emr_client):
    """
    Gets a list of steps for the specified cluster. In this example, all steps are
    returned, including completed and failed steps.

    :param cluster_id: The ID of the cluster.
    :param emr_client: The Boto3 EMR client object.
    :return: The list of steps for the specified cluster.
    """
    try:
        response = emr_client.list_steps(ClusterId=cluster_id)
        steps = response["Steps"]
        logger.info("Got %s steps for cluster %s.", len(steps), cluster_id)
    except ClientError:
        logger.exception("Couldn't get steps for cluster %s.", cluster_id)
        raise
    else:
        return steps

def parse_step_yaml_to_json(yaml_path, job_id):
    cwd = os.getcwd()
    yaml_path = os.path.join(cwd, yaml_path)
    with open(yaml_path, "r") as stream:
        steps_yaml = stream.read()
    parsed = yaml.safe_load(steps_yaml)
    steps = []
    
    for step in parsed['Steps']:
        args = ["spark-submit", "--deploy-mode", step["HadoopJarStep"]["Args"]["deploy-mode"]]

        for env_var in step["HadoopJarStep"]["Args"]["env"]:
            for key, val in env_var.items():
                args.extend(["--conf", f"{key}={val}"])
        args.extend(["--conf", f"spark.yarn.appMasterEnv.JOB_ID={job_id}"])

        args.append(step["HadoopJarStep"]["Args"]["script"])
        
        steps.append({
            "Name": f"{step['Name']}-{job_id}",
            "ActionOnFailure": step["ActionOnFailure"],
            "HadoopJarStep": {
                "Properties": [],
                "Jar": "command-runner.jar",
                "Args": args
            }
        })
    # create a dir compiled, exist ok

    compiled_dir = "orchestration/emr_jobs/download_px4_logs/compiled"
    compiled_path = os.path.join(cwd, compiled_dir)
    os.makedirs(compiled_dir, exist_ok=True)
    # get filename from yaml_path using splitext

    yaml_basename = os.path.splitext(os.path.basename(yaml_path))[0]
    compiled_json_filename = f"{yaml_basename}.json"
    compiled_path = os.path.join(compiled_dir, compiled_json_filename)
    with open(compiled_path, "w") as f:
        json.dump(steps, f, indent=4, sort_keys=True)
    return steps

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

if __name__ == "__main__":
    job_id = str(uuid4())
    name = f"FLIGHT-EMR-{job_id}"
    log_uri = f"s3://flight-emr/jobs/download_px4_logs/emr-logs/{job_id}/"
    keep_alive = False
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
                "Path": "s3://flight-emr/jobs/download_px4_logs/scripts/bootstrap.sh"
            },
        }
    ]

    steps = None
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    yaml_path = "orchestration/emr_jobs/download_px4_logs/steps.yaml"
    yaml_path = os.path.join(CURRENT_DIR, "steps.yaml")
    steps = parse_step_yaml_to_json(yaml_path, job_id=job_id)
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
    status_poller(
        "Waiting for cluster, this typically takes several minutes...",
        "RUNNING",
        lambda: describe_cluster(cluster_id, emr_client)["Status"]["State"],
    )
    status_poller(
        "Waiting for step to complete...",
        "COMPLETED",
        lambda: list_steps(cluster_id, emr_client)[0]["Status"]["State"],
    )
    status_poller(
        "Waiting for cluster to terminate.",
        "TERMINATED",
        lambda: describe_cluster(cluster_id, emr_client)["Status"]["State"],
    )


