from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow.utils.dates import days_ago

# EMR step script must be uploaded to S3
EMR_LOG_SCRIPT = "s3://flight-emr/scripts/download_logs.py"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
}

with DAG(
    dag_id="px4_log_download_emr",
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
) as dag:

    step = [
        {
            "Name": "Download PX4 Logs",
            "ActionOnFailure": "CONTINUE",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": ["spark-submit", EMR_LOG_SCRIPT]
            },
        }
    ]

    add_emr_step = EmrAddStepsOperator(
        task_id="add_emr_step",
        job_flow_id="j-9V0QPX8N69Y2",  # Replace with your EMR cluster ID
        steps=step,
    )

    watch_step = EmrStepSensor(
        task_id="watch_emr_step",
        job_flow_id="j-9V0QPX8N69Y2",
        step_id="{{ task_instance.xcom_pull(task_ids='add_emr_step', key='return_value')[0] }}",
    )

    add_emr_step >> watch_step
