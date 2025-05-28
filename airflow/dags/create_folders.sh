#!/bin/bash

# Create necessary directories for Airflow
mkdir -p /opt/airflow/dags
mkdir -p /opt/airflow/logs
mkdir -p /opt/airflow/plugins

# Set proper permissions
chmod -R 777 /opt/airflow/dags
chmod -R 777 /opt/airflow/logs
chmod -R 777 /opt/airflow/plugins

echo "Airflow directories created and permissions set."
