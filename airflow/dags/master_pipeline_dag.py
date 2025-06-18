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
    schedule_interval=None,  # Manual trigger only - individual DAGs have their own schedules
    catchup=False,
    tags=['bigdata5', 'master', 'ETL'],
    description='Master pipeline untuk orchestrasi seluruh proses ETL Big Data Kelompok 5 (Manual trigger)'
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
    
    # Trigger transformation pipelines setelah extraction selesai
    trigger_financial_transformation = TriggerDagRunOperator(
        task_id='trigger_financial_transformation',
        trigger_dag_id='transform_financial_reports_pipeline',
        wait_for_completion=True,
        poke_interval=60,
        execution_timeout=timedelta(hours=2),  # 2 hours timeout untuk transformasi financial
    )
    
    trigger_news_transformation = TriggerDagRunOperator(
        task_id='trigger_news_transformation',
        trigger_dag_id='transform_news_summary_pipeline',
        wait_for_completion=True,
        poke_interval=60,
        execution_timeout=timedelta(hours=2),  # 2 hours timeout untuk transformasi news
    )
    
    # Dependencies: Extraction harus selesai sebelum transformasi
    # News transformation depends on berita and yfinance extraction
    [trigger_yfinance_extraction, trigger_berita_extraction] >> trigger_news_transformation
    
    # Financial transformation depends on lapkeu extraction
    trigger_lapkeu_extraction >> trigger_financial_transformation
