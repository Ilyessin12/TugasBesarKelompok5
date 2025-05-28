from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

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
    'master_data_pipeline',
    default_args=default_args,
    description='Master pipeline that orchestrates all data workflows',
    schedule_interval='0 0 * * *',  # Run daily at midnight
    start_date=days_ago(1),
    catchup=False,
    tags=['master', 'pipeline'],
)

# Start task
start = DummyOperator(
    task_id='start_pipeline',
    dag=dag,
)

# End task
end = DummyOperator(
    task_id='end_pipeline',
    dag=dag,
)

# Trigger news scraping DAG
trigger_news_scraping = TriggerDagRunOperator(
    task_id='trigger_news_scraping',
    trigger_dag_id='news_scraping_pipeline',
    wait_for_completion=True,
    dag=dag,
)

# Trigger YFinance scraping DAG
trigger_yfinance_scraping = TriggerDagRunOperator(
    task_id='trigger_yfinance_scraping',
    trigger_dag_id='yfinance_scraping_pipeline',
    wait_for_completion=True,
    dag=dag,
)

# Trigger financial report scraping DAG (only on Mondays)
trigger_financial_report = TriggerDagRunOperator(
    task_id='trigger_financial_report',
    trigger_dag_id='financial_report_pipeline',
    wait_for_completion=True,
    execution_date="{{ execution_date if execution_date.weekday() == 0 else None }}",
    dag=dag,
)

# Trigger data transformation DAG
trigger_transformation = TriggerDagRunOperator(
    task_id='trigger_transformation',
    trigger_dag_id='data_transformation_pipeline',
    wait_for_completion=True,
    dag=dag,
)

# Set task dependencies
start >> [trigger_news_scraping, trigger_yfinance_scraping, trigger_financial_report]
[trigger_news_scraping, trigger_yfinance_scraping, trigger_financial_report] >> trigger_transformation
trigger_transformation >> end
