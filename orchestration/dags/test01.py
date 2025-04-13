from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def say_hello():
    print(f"Hello, Airflow! The current system time is {datetime.now().strftime('%m/%d/%y %H:%M')}.")

# Define default arguments for the DAG
default_args = {
    'start_date': datetime(2025, 4, 5),
    'catchup': False  # Prevents backfilling
}

# Initialize the DAG
with DAG(
    dag_id='hello_world_dag',
    default_args=default_args,
    schedule_interval='@daily',
    tags=['example'],
    description='My first Airflow DAG',
) as dag:

    hello_task = PythonOperator(
        task_id='say_hello_task',
        python_callable=say_hello
    )

    hello_task  # This sets the task execution order

