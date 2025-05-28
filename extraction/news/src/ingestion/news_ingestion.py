"""
Module for ingesting news data into MongoDB.
"""

import os
import time
import json
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv

from src.news.utils.mongo_utils import connect_to_mongodb, create_index, check_for_duplicates, bulk_insert_with_retry
from src.news.utils.common_utils import load_from_json, clean_cache

# Load environment variables
load_dotenv(find_dotenv(raise_error_if_not_found=True))

class NewsIngestion:
    """
    Class for ingesting news data into MongoDB.
    """
    
    def __init__(self):
        """
        Initialize the news ingestion module.
        """
        # load_dotenv() # Already loaded at module level
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.db_name = os.getenv("MONGODB_DATABASE_NAME")
        self.collection_name = os.getenv("COLLECTION_NEWS_DATA")
        self.news_output_prefix = os.getenv("NEWS_OUTPUT_PREFIX") # e.g., /app/cache/news/news_data_
        self.logger = logging.getLogger(__name__)

    def ingest(self) -> int:
        """
        Ingest news data from JSON files into MongoDB.
        
        Returns:
            int: Number of records ingested.
        """
        all_news_data = []
        
        # Load data from files (e.g., news_data_1, news_data_2, ...)
        # Ensure NEWS_OUTPUT_PREFIX in .env is like /app/cache/news/news_data_
        if not self.news_output_prefix:
            self.logger.error("NEWS_OUTPUT_PREFIX is not set in environment variables.")
            return 0
            
        for i in range(1, 6):  # Assuming 5 files like news_data_1 to news_data_5
            file_path = f"{self.news_output_prefix}{i}" # Corrected: remove .json
            
            if os.path.exists(file_path):
                self.logger.info(f"Loading news data from {file_path}")
                data = load_from_json(file_path)
                if data:
                    all_news_data.extend(data)
            else:
                self.logger.warning(f"File not found: {file_path}")
        
        self.logger.info(f"Loaded total of {len(all_news_data)} news records from all files")
        
        if not all_news_data:
            self.logger.warning("No news data found to ingest.")
            return 0
        
        client, db = connect_to_mongodb()
        
        try:
            collection = db[self.collection_name]
            create_index(collection, [("Emiten", 1), ("Date", 1), ("Title", 1)], unique=True)
            
            new_records = check_for_duplicates(collection, all_news_data, ["Emiten", "Date", "Title"])
            
            if not new_records:
                self.logger.info("No new records to insert.")
                return 0
            
            inserted_count = bulk_insert_with_retry(collection, new_records)
            self.logger.info(f"Successfully inserted {inserted_count} new records.")
            
            # Clean cache after successful ingestion
            # Ensure news_output_prefix is like /app/cache/news/news_data_
            # os.path.dirname will give /app/cache/news
            cache_dir_to_clean = os.path.dirname(f"{self.news_output_prefix}1")
            if os.path.exists(cache_dir_to_clean):
                 clean_cache(cache_dir_to_clean, exclude=[".gitkeep"]) # Adjust exclude if needed
            
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"Error during ingestion: {e}")
            return 0
        
        finally:
            if client:
                client.close()

def main():
    """
    Main function to run the news ingestion.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    ingestion = NewsIngestion()
    ingestion.ingest()

if __name__ == "__main__":
    main()