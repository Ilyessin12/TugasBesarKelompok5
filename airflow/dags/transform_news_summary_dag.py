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
    dag_id='transform_news_summary_pipeline',
    default_args=default_args,
    schedule_interval='@daily',  # Daily - same as berita_extraction
    catchup=False,
    tags=['bigdata5', 'transformation', 'news'],
    description='Pipeline untuk transformasi ringkasan berita'
) as dag:
    
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
