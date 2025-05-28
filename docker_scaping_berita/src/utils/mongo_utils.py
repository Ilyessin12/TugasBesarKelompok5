"""
MongoDB utility functions.
"""

import os
import time
import logging
from typing import List, Dict, Any, Tuple, Union
import pymongo
from pymongo import MongoClient
from pymongo.errors import PyMongoError, BulkWriteError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger
logger = logging.getLogger(__name__)

def connect_to_mongodb() -> Tuple[MongoClient, pymongo.database.Database]:
    """
    Connect to MongoDB using connection string from environment variable.
    
    Returns:
        tuple: (MongoClient, database)
    """
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    db_name = os.getenv("MONGODB_DATABASE_NAME")
    
    if not connection_string:
        raise ValueError("MongoDB connection string not found in environment variables")
    
    if not db_name:
        raise ValueError("MongoDB database name not found in environment variables")
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client[db_name]
        
        # Check connection
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB database: {db_name}")
        
        return client, db
    
    except PyMongoError as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def create_index(collection: pymongo.collection.Collection, 
                 fields: List[Tuple[str, int]], 
                 unique: bool = True) -> None:
    """
    Create an index on a collection if it doesn't already exist.
    """
    # Cek index yang ada
    existing_indexes = collection.index_information()
    
    # Cek apakah ada index dengan field yang sama
    field_names = [f[0] for f in fields]
    for index_name, index_info in existing_indexes.items():
        if index_name == '_id_':  # Skip default index
            continue
            
        existing_fields = [key for key, _ in index_info['key']]
        if existing_fields == field_names:
            logger.info(f"Using existing index '{index_name}'")
            return
    
    # Jika tidak ada index yang cocok, buat baru
    try:
        index_name = "_".join(field_names)
        collection.create_index(fields, unique=unique, name=index_name)
        logger.info(f"Created new index '{index_name}'")
    except PyMongoError as e:
        logger.error(f"Failed to create index: {e}")
        raise


def check_for_duplicates(collection: pymongo.collection.Collection,
                         records: List[Dict[str, Any]],
                         unique_fields: List[str]) -> List[Dict[str, Any]]:
    """
    Filter out records that already exist in the collection.
    
    Args:
        collection: MongoDB collection
        records: List of records to check
        unique_fields: Fields that determine uniqueness
        
    Returns:
        list: Records that don't already exist in the collection
    """
    # Create a list to store new records
    new_records = []
    
    # Check each record
    for record in records:
        # Create a query using the unique fields
        query = {field: record[field] for field in unique_fields if field in record}
        
        # Check if a document with these values already exists
        existing = collection.find_one(query)
        
        if not existing:
            new_records.append(record)
    
    logger.info(f"Found {len(new_records)} new records out of {len(records)} total records")
    
    return new_records


def bulk_insert_with_retry(collection: pymongo.collection.Collection,
                           records: List[Dict[str, Any]],
                           max_retries: int = 3,
                           delay: int = 5) -> int:
    """
    Insert multiple records with retry mechanism.
    
    Args:
        collection: MongoDB collection
        records: List of records to insert
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        int: Number of records inserted
    """
    if not records:
        logger.warning("No records to insert")
        return 0
    
    for attempt in range(max_retries):
        try:
            # Insert records
            result = collection.insert_many(records, ordered=False)
            return len(result.inserted_ids)
        
        except BulkWriteError as e:
            # Extract successful operations count
            write_errors = e.details.get('writeErrors', [])
            successful_inserts = len(records) - len(write_errors)
            
            # Some records inserted successfully, some failed
            logger.warning(f"Partial bulk insert: {successful_inserts} inserted, {len(write_errors)} failed")
            
            # Process specific errors
            for error in write_errors:
                if error.get('code') == 11000:  # Duplicate key error
                    logger.debug(f"Duplicate key error: {error}")
                else:
                    logger.warning(f"Write error: {error}")
            
            return successful_inserts
        
        except PyMongoError as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Maximum retry attempts reached")
                raise
    
    return 0  # Should not reach here 