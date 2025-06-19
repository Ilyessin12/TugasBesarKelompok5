import os
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 6, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='yfinance_extraction_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['bigdata5', 'extraction', 'yfinance'],
    description='Pipeline untuk ekstraksi data YFinance'
) as dag:
    
    # Task untuk ekstraksi data YFinance
    extract_yfinance = DockerOperator(
        task_id='extract_yfinance_data',
        image='tugasbesarkelompok5-yfinance-scraper:latest',
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="app-network",
        mount_tmp_dir=False,
        container_name="airflow_yfinance_extract_{{ ts_nodash }}",
        environment={
            'MONGODB_CONNECTION_STRING': os.environ.get('MONGODB_CONNECTION_STRING'),
            'MONGODB_DATABASE_NAME': os.environ.get('MONGODB_DATABASE_NAME'),
            'COLLECTION_YFINANCE_DATA': os.environ.get('COLLECTION_YFINANCE_DATA'),
            'YFINANCE_OUTPUT': os.environ.get('YFINANCE_OUTPUT', 'yfinancescrape.json'),
            'MONGODB_BATCH_SIZE': os.environ.get('MONGODB_BATCH_SIZE', '20'),
            'COMPANY_PROCESSING_DELAY': os.environ.get('COMPANY_PROCESSING_DELAY', '2'),
            'MAX_COMPANIES_TO_PROCESS': os.environ.get('MAX_COMPANIES_TO_PROCESS', '5'),
        },
    )
