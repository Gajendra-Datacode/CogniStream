from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


def run_cognistream_pipeline():
    print("Starting CogniStream data pipeline...")
    print("Checking developer activity events...")
    print("Processing activity data...")
    print("CogniStream pipeline completed successfully!")


default_args = {
    "owner": "cognistream",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="cognistream_pipeline",
    default_args=default_args,
    description="CogniStream developer activity analytics workflow",
    start_date=datetime(2026, 11, 18),
    schedule="@daily",
    catchup=False,
    tags=["cognistream", "analytics"],
) as dag:

    run_pipeline = PythonOperator(
        task_id="run_cognistream_pipeline",
        python_callable=run_cognistream_pipeline,
    )