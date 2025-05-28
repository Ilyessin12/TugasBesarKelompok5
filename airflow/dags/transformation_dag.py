from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'data_transformation_pipeline',
    default_args=default_args,
    description='Pipeline for transforming scraped data',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
    tags=['transformation', 'data'],
)

# Task to run the data transformation in Docker
transform_data = DockerOperator(
    task_id='transform_data',
    image='bigdata5-transform',
    container_name='airflow_data_transformation',
    api_version='auto',
    auto_remove=True,
    command='python /app/src/main.py',
    docker_url='unix://var/run/docker.sock',
    network_mode='app-network',
    environment={
        'MONGODB_CONNECTION_STRING': '{{var.value.mongodb_connection_string}}',
        'MONGODB_DATABASE_NAME': '{{var.value.mongodb_database_name}}',
        'COLLECTION_NEWS_DATA': '{{var.value.collection_news_data}}',
        'COLLECTION_NEWS_SUMMARY_DATA': '{{var.value.collection_news_summary_data}}',
        'COLLECTION_FINANCIAL_REPORTS': '{{var.value.collection_financial_reports}}',
        'GEMINI_API_KEY': '{{var.value.gemini_api_key}}'
    },
    dag=dag,
)

# Set task dependencies
transform_data
