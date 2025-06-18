import os
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 6, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='bigdata5_master_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['bigdata5', 'master', 'ETL'],
    description='Master pipeline untuk orchestrasi seluruh proses ETL Big Data Kelompok 5'
) as dag:
    
    # Trigger extraction pipelines
    trigger_yfinance_extraction = TriggerDagRunOperator(
        task_id='trigger_yfinance_extraction',
        trigger_dag_id='yfinance_extraction_pipeline',
        wait_for_completion=True,
        poke_interval=30,
        execution_timeout=timedelta(hours=1),  # 1 hour timeout
    )
    
    trigger_berita_extraction = TriggerDagRunOperator(
        task_id='trigger_berita_extraction',
        trigger_dag_id='berita_extraction_pipeline',
        wait_for_completion=True,
        poke_interval=30,
        execution_timeout=timedelta(hours=1),
    )
    
    trigger_lapkeu_extraction = TriggerDagRunOperator(
        task_id='trigger_lapkeu_extraction',
        trigger_dag_id='laporan_keuangan_extraction_pipeline',
        wait_for_completion=True,
        poke_interval=30,
        execution_timeout=timedelta(hours=2),  # 2 hours timeout untuk laporan keuangan (lebih lama)
    )
    
    # Trigger transformation pipeline setelah extraction selesai
    trigger_transformation = TriggerDagRunOperator(
        task_id='trigger_transformation',
        trigger_dag_id='transformation_pipeline',
        wait_for_completion=True,
        poke_interval=60,
        execution_timeout=timedelta(hours=2),  # 2 hours timeout untuk transformasi
    )
    
    # Dependencies: Semua extraction harus selesai sebelum transformasi
    [trigger_yfinance_extraction, trigger_berita_extraction, trigger_lapkeu_extraction] >> trigger_transformation
