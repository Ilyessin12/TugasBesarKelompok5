#!/bin/bash
set -e

# Setup Airflow
airflow db init

# Create default admin user if it doesn't exist
airflow users list | grep -q "admin" || (
    airflow users create \
        --username admin \
        --password admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com
)

# Create necessary connections
# MongoDB connection
airflow connections add 'mongodb_default' \
    --conn-type 'mongo' \
    --conn-host 'mongodb' \
    --conn-port '27017' \
    --conn-login '' \
    --conn-password ''

# Start Airflow services
exec airflow webserver
