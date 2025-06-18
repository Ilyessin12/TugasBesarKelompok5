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
    dag_id='transformation_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['bigdata5', 'transformation'],
    description='Pipeline untuk transformasi data financial reports dan news summary'
) as dag:
    
    # Task untuk transformasi laporan keuangan
    transform_financial_reports = DockerOperator(
        task_id='transform_financial_reports',
        image='tugasbesarkelompok5-transform:latest',
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="app-network",
        mount_tmp_dir=False,
        container_name="airflow_transform_financial_{{ ts_nodash }}",
        environment={
            'MONGODB_CONNECTION_STRING': os.environ.get('MONGODB_CONNECTION_STRING'),
            'MONGODB_DATABASE_NAME': os.environ.get('MONGODB_DATABASE_NAME'),
            'COLLECTION_FINANCIAL_REPORTS': os.environ.get('COLLECTION_FINANCIAL_REPORTS'),
            'MONGO_OUTPUT_COLLECTION': 'Docker_Transformasi_Laporan_Keuangan',
            'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY'),
            'CHECKPOINT_INTERVAL': '150'
        },
        command='python3 /app/src/financialreport_transformer.py'
    )
    
    # Task untuk transformasi ringkasan berita
    transform_news_summary = DockerOperator(
        task_id='transform_news_summary',
        image='tugasbesarkelompok5-transform:latest',
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="app-network",
        mount_tmp_dir=False,
        container_name="airflow_transform_news_{{ ts_nodash }}",
        environment={
            'MONGODB_CONNECTION_STRING': os.environ.get('MONGODB_CONNECTION_STRING'),
            'MONGODB_DATABASE_NAME': os.environ.get('MONGODB_DATABASE_NAME'),
            'COLLECTION_NEWS_DATA': os.environ.get('COLLECTION_NEWS_DATA'),
            'COLLECTION_NEWS_SUMMARY_DATA': os.environ.get('COLLECTION_NEWS_SUMMARY_DATA'),
            'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY'),
            'CHECKPOINT_INTERVAL': '100'
        },
        command='python3 /app/src/news_transformer.py'
    )
    
    # Dependencies: kedua task bisa berjalan paralel
    [transform_financial_reports, transform_news_summary]
