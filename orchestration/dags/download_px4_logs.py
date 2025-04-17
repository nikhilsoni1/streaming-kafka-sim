from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

with DAG(
    dag_id='download_px4_logs_pipeline',
    default_args=default_args,
    description='Runs PX4 log download after setting environment',
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    start_date=days_ago(1),
    catchup=False,
    tags=['px4', 'emr', 'logs']
) as dag:

    run_env_script = BashOperator(
        task_id='run_env_script',
        bash_command="/opt/airflow/orchestration/emr_jobs/download_px4_logs/ship_env.sh ",
        dag=dag
    )

    run_log_download = BashOperator(
        task_id='run_log_download',
        bash_command='python3 /opt/airflow/orchestration/emr_jobs/download_px4_logs/launch.py ',
        dag=dag
    )

    run_env_script >> run_log_download
