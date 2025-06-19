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
    dag_id='berita_extraction_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['bigdata5', 'extraction', 'berita'],
    description='Pipeline untuk ekstraksi data berita'
) as dag:
    
    # Task untuk ekstraksi berita
    extract_berita = DockerOperator(
        task_id='extract_berita_data',
        image='tugasbesarkelompok5-berita-scraper:latest',
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="app-network",
        mount_tmp_dir=False,
        container_name="airflow_berita_extract_{{ ts_nodash }}",
        environment={
            'MONGODB_CONNECTION_STRING': os.environ.get('MONGODB_CONNECTION_STRING'),
            'MONGODB_DATABASE_NAME': os.environ.get('MONGODB_DATABASE_NAME'),
            'COLLECTION_NEWS': os.environ.get('COLLECTION_NEWS'),
            'NEWS_OUTPUT_PREFIX': os.environ.get('NEWS_OUTPUT_PREFIX', 'news_data_pt'),
            'MONGODB_BATCH_SIZE': os.environ.get('MONGODB_BATCH_SIZE', '20'),
            'COMPANY_PROCESSING_DELAY': os.environ.get('COMPANY_PROCESSING_DELAY', '2'),
            'MAX_COMPANIES_TO_PROCESS': os.environ.get('MAX_COMPANIES_TO_PROCESS', '5'),
        },
    )
