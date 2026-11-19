import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add scripts folder to Python path
sys.path.insert(0, "/opt/airflow/scripts")

from airflow_pipeline import process_activity_data


default_args = {
    "owner": "cognistream",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="cognistream_pipeline",
    default_args=default_args,
    description="Developer activity data processing pipeline",
    start_date=datetime(2026, 11, 18),
    schedule="@daily",
    catchup=False,
    tags=["cognistream", "polars", "analytics"],
) as dag:

    process_data = PythonOperator(
        task_id="process_activity_data",
        python_callable=process_activity_data,
    )

    process_data