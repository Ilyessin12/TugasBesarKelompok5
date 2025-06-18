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
    dag_id='transform_financial_reports_pipeline',
    default_args=default_args,
    schedule_interval='0 0 1 */3 *',  # Every 3 months (quarterly) - same as laporan_keuangan
    catchup=False,
    tags=['bigdata5', 'transformation', 'financial'],
    description='Pipeline untuk transformasi data financial reports'
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
