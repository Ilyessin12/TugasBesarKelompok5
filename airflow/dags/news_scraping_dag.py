from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
import os
import json

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
    'news_scraping_pipeline',
    default_args=default_args,
    description='Pipeline for scraping news data',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
    tags=['scraping', 'news'],
)

# Try to load environment variables from Airflow Variables
try:
    # Load MongoDB connection details from Airflow Variables
    mongodb_conn_string = Variable.get("mongodb_connection_string", 
                                      default="mongodb://mongodb:27017")
    mongodb_db_name = Variable.get("mongodb_database_name", 
                                  default="Big_Data_kel_5")
except Exception as e:
    # Fallback values if Variables not found
    mongodb_conn_string = "mongodb://mongodb:27017"
    mongodb_db_name = "Big_Data_kel_5"

# Define environment variables to pass to Docker container
docker_env_vars = {
    'MONGODB_CONNECTION_STRING': mongodb_conn_string,
    'MONGODB_DATABASE_NAME': mongodb_db_name,
    'COLLECTION_NEWS_DATA': 'Docker_Scraping_Berita',
    'CACHE_DIR': '/app/cache',
    'NEWS_OUTPUT_PREFIX': '/app/cache/news/news_data_',
    'CHROME_URL': 'http://selenium-chrome-berita:4444/wd/hub',
    'SELENIUM_TIMEOUT': '30',
    'MAX_RETRY_ATTEMPTS': '3',
    'RETRY_DELAY': '5'
}

# Task to run the news scraper in Docker
scrape_news = DockerOperator(
    task_id='scrape_news',
    image='bigdata5-scraping-berita',
    container_name='airflow_news_scraper',
    api_version='auto',
    auto_remove=True,
    command='python /app/scripts/main.py --mode scrape',
    docker_url='unix://var/run/docker.sock',
    environment=docker_env_vars,
    network_mode='bridge',  # Use bridge instead of custom network
    extra_hosts={
        'selenium-chrome-berita': 'host-gateway'  # Connect to Selenium host
    },
    mounts=[
        # Mount Docker socket to enable Docker-in-Docker
        {'source': '/var/run/docker.sock', 
         'target': '/var/run/docker.sock', 
         'type': 'bind'},
        # Mount cache directory for persistent storage
        {'source': '/opt/airflow/cache/news', 
         'target': '/app/cache/news', 
         'type': 'bind'}
    ],
    mount_tmp_dir=False,
    dag=dag,
)

# Task to run the news ingestion in Docker
ingest_news = DockerOperator(
    task_id='ingest_news',
    image='bigdata5-scraping-berita',
    container_name='airflow_news_ingestion',
    api_version='auto',
    auto_remove=True,
    command='python /app/scripts/main.py --mode ingest',
    docker_url='unix://var/run/docker.sock',
    environment=docker_env_vars,
    network_mode='bridge',  # Use bridge instead of custom network
    mounts=[
        # Mount Docker socket to enable Docker-in-Docker
        {'source': '/var/run/docker.sock', 
         'target': '/var/run/docker.sock', 
         'type': 'bind'},
        # Mount cache directory for persistent storage
        {'source': '/opt/airflow/cache/news', 
         'target': '/app/cache/news', 
         'type': 'bind'}
    ],
    mount_tmp_dir=False,
    dag=dag,
)

# Set task dependencies
scrape_news >> ingest_news