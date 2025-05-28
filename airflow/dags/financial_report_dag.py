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
    'financial_report_pipeline',
    default_args=default_args,
    description='Pipeline for scraping financial reports',
    schedule_interval=timedelta(days=7),  # Weekly schedule
    start_date=days_ago(1),
    catchup=False,
    tags=['scraping', 'financial', 'reports'],
)

# Task to run the financial report scraper in Docker
scrape_financial_reports = DockerOperator(
    task_id='scrape_financial_reports',
    image='bigdata5-scraping-laporan-keuangan',
    container_name='airflow_financial_scraper',
    api_version='auto',
    auto_remove=True,
    command='python /app/scripts/main.py --mode scrape',
    docker_url='unix://var/run/docker.sock',
    network_mode='scraper-finance-network',
    dag=dag,
)

# Task to run the financial report ingestion in Docker
ingest_financial_reports = DockerOperator(
    task_id='ingest_financial_reports',
    image='bigdata5-scraping-laporan-keuangan',
    container_name='airflow_financial_ingestion',
    api_version='auto',
    auto_remove=True,
    command='python /app/scripts/main.py --mode ingest',
    docker_url='unix://var/run/docker.sock',
    network_mode='scraper-finance-network',
    dag=dag,
)

# Set task dependencies
scrape_financial_reports >> ingest_financial_reports
