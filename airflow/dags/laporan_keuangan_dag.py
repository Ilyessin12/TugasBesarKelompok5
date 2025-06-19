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
    dag_id='laporan_keuangan_extraction_pipeline',
    default_args=default_args,
    schedule_interval='0 0 1 */3 *',  # Every 3 months (quarterly)
    catchup=False,
    tags=['bigdata5', 'extraction', 'laporan-keuangan'],
    description='Pipeline untuk ekstraksi laporan keuangan'
) as dag:
    
    # Task untuk ekstraksi laporan keuangan
    extract_lapkeu = DockerOperator(
        task_id='extract_laporan_keuangan',
        image='tugasbesarkelompok5-lapkeu-scraper:latest',
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="app-network",
        mount_tmp_dir=False,
        container_name="airflow_lapkeu_extract_{{ ts_nodash }}",
        environment={
            'MONGODB_CONNECTION_STRING': os.environ.get('MONGODB_CONNECTION_STRING'),
            'MONGODB_DATABASE_NAME': os.environ.get('MONGODB_DATABASE_NAME'),
            'COLLECTION_FINANCIAL_REPORTS': os.environ.get('COLLECTION_FINANCIAL_REPORTS'),
            'BASE_DOWNLOAD_DIR': os.environ.get('BASE_DOWNLOAD_DIR', 'downloads'),
            'FINANCIAL_REPORTS_OUTPUT': os.environ.get('FINANCIAL_REPORTS_OUTPUT', 'financial_reports.json'),
            'MONGODB_BATCH_SIZE': os.environ.get('MONGODB_BATCH_SIZE', '20'),
            'COMPANY_PROCESSING_DELAY': os.environ.get('COMPANY_PROCESSING_DELAY', '2'),
            'MAX_COMPANIES_TO_PROCESS': os.environ.get('MAX_COMPANIES_TO_PROCESS', '5'),
        },
    )
