import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, "/opt/airflow/scripts")

from airflow_pipeline import process_activity_data
from analytics_report import generate_analytics_report


default_args = {
    "owner": "cognistream",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="cognistream_pipeline",
    default_args=default_args,
    description="CogniStream data processing and analytics pipeline",
    start_date=datetime(2026, 11, 18),
    schedule="@daily",
    catchup=False,
    tags=["cognistream", "polars", "clickhouse", "analytics"],
) as dag:

    # Task 1: Process and load activity data
    process_data = PythonOperator(
        task_id="process_activity_data",
        python_callable=process_activity_data,
    )

    # Task 2: Generate analytics reports
    generate_report = PythonOperator(
        task_id="generate_analytics_report",
        python_callable=generate_analytics_report,
    )

    # Workflow dependency
    process_data >> generate_report