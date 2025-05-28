from airflow.plugins_manager import AirflowPlugin
from operators.mongodb_operator import MongoDBOperator

class BigDataPlugin(AirflowPlugin):
    name = "bigdata_plugin"
    operators = [MongoDBOperator]
