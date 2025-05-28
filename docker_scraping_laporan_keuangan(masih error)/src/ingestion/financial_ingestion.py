"""
Module for ingesting financial report data into MongoDB.
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

from ..utils.mongo_utils import connect_to_mongodb, create_index, bulk_insert_with_retry, bulk_update_with_retry
from ..utils.common_utils import load_from_json, clean_cache

class FinancialReportIngestion:
    """
    Class for ingesting financial report data into MongoDB.
    """
    
    def __init__(self):
        """
        Initialize the financial report ingestion module.
        """
        load_dotenv()
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        self.db_name = os.getenv("MONGODB_DATABASE_NAME")
        self.collection_name = os.getenv("COLLECTION_FINANCIAL_REPORTS")
        self.financial_reports_output = os.getenv("FINANCIAL_REPORTS_OUTPUT")
        self.base_download_dir = os.getenv("BASE_DOWNLOAD_DIR")
        self.logger = logging.getLogger(__name__)
    
    def ingest(self) -> Tuple[int, int]:
        """
        Ingest financial report data into MongoDB.
        
        Returns:
            Tuple[int, int]: Number of records inserted and updated
        """
        start_time = time.time()
        
        # Load data from JSON file
        self.logger.info("Loading data from JSON file...")
        try:
            all_financial_reports = load_from_json(self.financial_reports_output)
            if not all_financial_reports:
                self.logger.warning(f"No data found in {self.financial_reports_output}")
                return 0, 0
            
            self.logger.info(f"Loaded {len(all_financial_reports)} financial reports from JSON file")
        except FileNotFoundError:
            self.logger.error(f"Error: {self.financial_reports_output} not found!")
            return 0, 0
        except json.JSONDecodeError:
            self.logger.error(f"Error: Invalid JSON format in {self.financial_reports_output}!")
            return 0, 0
        
        # Connect to MongoDB
        client, db = connect_to_mongodb()
        
        try:
            # Select collection
            collection = db[self.collection_name]
            
            # Create index for faster lookups if it doesn't exist
            create_index(collection, [("company", 1)], unique=True)
            
            # Get all existing company records in one query
            self.logger.info("Fetching existing records...")
            existing_companies = set()
            for doc in collection.find({}, {"company": 1, "_id": 0}):
                existing_companies.add(doc["company"])
            
            self.logger.info(f"Found existing records for {len(existing_companies)} companies")
            
            # Prepare bulk operations
            inserts = []
            updates = []
            
            for record in all_financial_reports:
                company = record["company"]
                
                # Check if this company already exists
                if company in existing_companies:
                    # Update existing record
                    updates.append(({"company": company}, record))
                else:
                    # Insert new record
                    inserts.append(record)
                    existing_companies.add(company)  # Add to tracking set
            
            # Execute bulk operations with smaller batch size due to large documents
            batch_size = 20
            insert_count = 0
            update_count = 0
            
            # Process inserts
            for i in range(0, len(inserts), batch_size):
                batch = inserts[i:i+batch_size]
                if batch:
                    insert_count += bulk_insert_with_retry(collection, batch)
            
            # Process updates
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                if batch:
                    update_count += bulk_update_with_retry(collection, batch)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Completed MongoDB ingestion process. Inserted {insert_count} new records and updated {update_count} records in {elapsed_time:.2f} seconds")
            
            # Clean up cache directories after successful ingestion
            if insert_count > 0 or update_count > 0:
                self._clean_cache()
            
            return insert_count, update_count
        
        finally:
            # Close MongoDB connection
            client.close()
    
    def _clean_cache(self):
        """
        Clean up cache directories after successful ingestion.
        """
        # Clean up download directory
        if os.path.exists(self.base_download_dir):
            try:
                for item in os.listdir(self.base_download_dir):
                    item_path = os.path.join(self.base_download_dir, item)
                    if os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path)
                        self.logger.info(f"Removed directory: {item_path}")
                    elif os.path.isfile(item_path) and item != ".gitkeep":
                        os.remove(item_path)
                        self.logger.info(f"Removed file: {item_path}")
            except Exception as e:
                self.logger.error(f"Error cleaning cache: {e}")
        
        # Keep the JSON output file but clean up all other files
        output_dir = os.path.dirname(self.financial_reports_output)
        clean_cache(output_dir, exclude=[os.path.basename(self.financial_reports_output), ".gitkeep"])


def main():
    """
    Main function to run the financial report ingestion.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and run ingestion
    ingestion = FinancialReportIngestion()
    ingestion.ingest()


if __name__ == "__main__":
    main() 