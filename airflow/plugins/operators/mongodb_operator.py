from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from pymongo import MongoClient
import logging

class MongoDBOperator(BaseOperator):
    """
    Operator for interacting with MongoDB
    
    :param mongo_conn_id: connection id from Airflow connections
    :type mongo_conn_id: str
    :param database: database name
    :type database: str
    :param collection: collection name
    :type collection: str
    :param query: query to execute
    :type query: dict
    :param operation: operation to perform (find, insert, update, delete)
    :type operation: str
    :param update_data: data for update operation
    :type update_data: dict
    :param insert_data: data for insert operation
    :type insert_data: dict or list
    """
    
    @apply_defaults
    def __init__(
        self,
        mongo_conn_id='mongodb_default',
        database=None,
        collection=None,
        query=None,
        operation=None,
        update_data=None,
        insert_data=None,
        *args,
        **kwargs
    ):
        super(MongoDBOperator, self).__init__(*args, **kwargs)
        self.mongo_conn_id = mongo_conn_id
        self.database = database
        self.collection = collection
        self.query = query or {}
        self.operation = operation
        self.update_data = update_data
        self.insert_data = insert_data
        
    def execute(self, context):
        """
        Execute the MongoDB operation
        """
        from airflow.hooks.base_hook import BaseHook
        
        # Get MongoDB connection details
        conn = BaseHook.get_connection(self.mongo_conn_id)
        uri = f"mongodb://{conn.host}:{conn.port}"
        
        # Connect to MongoDB
        client = MongoClient(uri)
        db = client[self.database]
        collection = db[self.collection]
        
        # Execute operation
        if self.operation == 'find':
            result = list(collection.find(self.query))
            logging.info(f"Found {len(result)} documents")
            return result
            
        elif self.operation == 'insert':
            if isinstance(self.insert_data, list):
                result = collection.insert_many(self.insert_data)
                logging.info(f"Inserted {len(result.inserted_ids)} documents")
                return result.inserted_ids
            else:
                result = collection.insert_one(self.insert_data)
                logging.info(f"Inserted document with ID: {result.inserted_id}")
                return result.inserted_id
                
        elif self.operation == 'update':
            result = collection.update_many(self.query, self.update_data)
            logging.info(f"Updated {result.modified_count} documents")
            return result.modified_count
            
        elif self.operation == 'delete':
            result = collection.delete_many(self.query)
            logging.info(f"Deleted {result.deleted_count} documents")
            return result.deleted_count
            
        else:
            raise ValueError(f"Unsupported operation: {self.operation}")