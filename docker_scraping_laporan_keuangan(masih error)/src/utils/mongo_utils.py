"""
MongoDB utility functions for the financial report scraper.
"""

import os
import time
import logging
from typing import Dict, Any, List, Tuple
import pymongo
from pymongo import MongoClient, UpdateOne, InsertOne
from pymongo.errors import BulkWriteError, PyMongoError

def connect_to_mongodb():
    """
    Connect to MongoDB.
    
    Returns:
        (MongoClient, Database): MongoDB client and database
    """
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    db_name = os.getenv("MONGODB_DATABASE_NAME")
    
    try:
        client = MongoClient(
            connection_string,
            maxPoolSize=100,
            retryWrites=True
        )
        db = client[db_name]
        logging.info(f"Connected to MongoDB database: {db_name}")
        return client, db
    except PyMongoError as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

def create_index(collection, index_fields, unique=False):
    """
    Create an index in the collection if it does not exist.
    
    Args:
        collection: MongoDB collection
        index_fields: List of fields to index
        unique: Whether the index should be unique
    """
    # Check if index already exists
    existing_indexes = collection.index_information()
    index_name = "_".join([f"{field[0]}_{field[1]}" for field in index_fields])
    
    if index_name not in existing_indexes:
        try:
            collection.create_index(index_fields, unique=unique, background=True)
            logging.info(f"Created index on {index_fields}")
        except PyMongoError as e:
            logging.error(f"Error creating index: {e}")

def check_for_duplicates(collection, records, unique_fields):
    """
    Check for duplicates in the database based on unique fields.
    
    Args:
        collection: MongoDB collection
        records: List of records to check
        unique_fields: List of field names that form a unique key
        
    Returns:
        List of new records that don't exist in the database
    """
    new_records = []
    existing_keys = set()
    
    # Create a query to get all existing unique keys
    projection = {field: 1 for field in unique_fields}
    projection["_id"] = 0
    
    # Get all existing keys
    for doc in collection.find({}, projection):
        # Create a tuple of values for the unique fields
        key = tuple(doc.get(field) for field in unique_fields)
        existing_keys.add(key)
    
    # Check each record
    for record in records:
        key = tuple(record.get(field) for field in unique_fields)
        if key not in existing_keys:
            new_records.append(record)
            existing_keys.add(key)  # Add to set to avoid duplicates in the batch
    
    logging.info(f"Found {len(new_records)} new records out of {len(records)}")
    return new_records

def bulk_insert_with_retry(collection, records, max_retries=3):
    """
    Insert multiple records with retry mechanism.
    
    Args:
        collection: MongoDB collection
        records: List of records to insert
        max_retries: Maximum number of retries
        
    Returns:
        int: Number of inserted records
    """
    if not records:
        return 0
    
    for retry in range(max_retries):
        try:
            result = collection.insert_many(records, ordered=False)
            return len(result.inserted_ids)
        except BulkWriteError as e:
            # Some documents may have been inserted successfully
            inserted = e.details.get("nInserted", 0)
            if inserted > 0:
                logging.warning(f"Partial insert: {inserted} records inserted, retrying the rest")
            
            # Get the records that failed
            records = [record for record in records if record not in e.details.get("writeConcernErrors", [])]
            
            if not records or retry == max_retries - 1:
                logging.error(f"Failed to insert all records after {retry + 1} attempts")
                return inserted
            
            logging.warning(f"Retrying insert for {len(records)} records (attempt {retry + 1})")
            time.sleep(2)  # Wait before retrying
        except PyMongoError as e:
            logging.error(f"MongoDB error on insert: {e}")
            if retry == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retrying
    
    return 0

def bulk_update_with_retry(collection, updates, max_retries=3):
    """
    Update multiple records with retry mechanism.
    
    Args:
        collection: MongoDB collection
        updates: List of (filter, update) tuples
        max_retries: Maximum number of retries
        
    Returns:
        int: Number of updated records
    """
    if not updates:
        return 0
    
    # Convert to UpdateOne objects
    operations = [UpdateOne(filter_doc, {"$set": update_doc}) for filter_doc, update_doc in updates]
    
    for retry in range(max_retries):
        try:
            result = collection.bulk_write(operations, ordered=False)
            return result.modified_count
        except BulkWriteError as e:
            # Some documents may have been updated successfully
            modified = e.details.get("nModified", 0)
            if modified > 0:
                logging.warning(f"Partial update: {modified} records updated, retrying the rest")
            
            # Get the operations that failed
            failed_indices = [err["index"] for err in e.details.get("writeErrors", [])]
            operations = [op for i, op in enumerate(operations) if i not in failed_indices]
            
            if not operations or retry == max_retries - 1:
                logging.error(f"Failed to update all records after {retry + 1} attempts")
                return modified
            
            logging.warning(f"Retrying update for {len(operations)} records (attempt {retry + 1})")
            time.sleep(2)  # Wait before retrying
        except PyMongoError as e:
            logging.error(f"MongoDB error on update: {e}")
            if retry == max_retries - 1:
                raise
            time.sleep(2)  # Wait before retrying
    
    return 0 