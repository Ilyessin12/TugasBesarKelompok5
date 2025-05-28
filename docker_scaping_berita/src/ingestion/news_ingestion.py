"""
Module for ingesting news data into MongoDB.
"""

import os
import time
import json
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from ..utils.mongo_utils import connect_to_mongodb, create_index, check_for_duplicates, bulk_insert_with_retry
from ..utils.common_utils import load_from_json, clean_cache

class NewsIngestion:
    """
    Class for ingesting news data into MongoDB.
    """
    
    def __init__(self):
        """
        Initialize the news ingestion module.
        """
        load_dotenv()
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.db_name = os.getenv("MONGODB_DATABASE_NAME")
        self.collection_name = os.getenv("COLLECTION_NEWS_DATA")
        self.news_output_prefix = os.getenv("NEWS_OUTPUT_PREFIX")
        self.logger = logging.getLogger(__name__)
    
    def ingest(self) -> int:
        """
        Ingest news data into MongoDB.
        
        Returns:
            int: Number of records inserted
        """
        start_time = time.time()
        
        # Load data from all JSON files
        self.logger.info("Loading data from JSON files...")
        all_news_data = []
        
        for i in range(1, 6):
            file_name = f"{self.news_output_prefix}{i}"
            try:
                news_data = load_from_json(file_name)
                if news_data:
                    all_news_data.extend(news_data)
                    self.logger.info(f"Loaded {len(news_data)} records from {file_name}")
            except FileNotFoundError:
                self.logger.warning(f"Warning: {file_name} not found. Skipping...")
            except json.JSONDecodeError:
                self.logger.warning(f"Warning: Invalid JSON format in {file_name}. Skipping...")
        
        self.logger.info(f"Loaded total of {len(all_news_data)} news records from all files")
        
        # If no data found, return
        if not all_news_data:
            self.logger.warning("No news data found to ingest.")
            return 0
        
        # Connect to MongoDB
        client, db = connect_to_mongodb()
        
        try:
            # Select collection
            collection = db[self.collection_name]
            
            # Create compound index for faster lookups if it doesn't exist
            create_index(collection, [("Emiten", 1), ("Date", 1), ("Title", 1)], unique=True)
            
            # Filter out duplicates
            unique_fields = ["Emiten", "Date", "Title"]
            new_records = check_for_duplicates(collection, all_news_data, unique_fields)
            
            if not new_records:
                self.logger.info("No new records to insert.")
                return 0
            
            # Insert new records with retry mechanism
            inserted_count = bulk_insert_with_retry(collection, new_records)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Completed MongoDB ingestion process. Inserted {inserted_count} new records in {elapsed_time:.2f} seconds")
            
            # Clean cache files after successful ingestion
            if inserted_count > 0:
                cache_dir = os.path.dirname(self.news_output_prefix)
                clean_cache(cache_dir)
            
            return inserted_count
        
        finally:
            # Close MongoDB connection
            client.close()


def main():
    """
    Main function to run the news ingestion.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and run ingestion
    ingestion = NewsIngestion()
    ingestion.ingest()


if __name__ == "__main__":
    main() 