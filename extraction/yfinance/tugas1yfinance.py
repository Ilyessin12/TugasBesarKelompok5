#!/usr/bin/env python3
"""
Stock Data Scraping and MongoDB Ingestion Script
This script scrapes stock data using yfinance and ingests it into MongoDB
"""

# ========================================
# Import Libraries
# ========================================

# Library untuk mengambil data tabular dari yfinance
import yfinance as yf

# Library untuk HTTP requests dan parsing HTML
import requests
from bs4 import BeautifulSoup

# Library untuk parsing file XML
import xml.etree.ElementTree as ET

# Library untuk mengekstrak file ZIP (misalnya instance.zip)
import zipfile

# Library untuk koneksi ke MongoDB
import pymongo

# Library tambahan (opsional) seperti untuk pengolahan data dan logging
import pandas as pd
import os
import logging

import json
from datetime import datetime

# Library untuk load .env file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Library untuk fungsi waktu
import time


def scrape_stock_data():
    """
    Scraping Data
    
    Setelah import library maka akan dilakukan proses pengambilan data menggunakan yfinance 
    lalu disimpan dalam bentuk json
    """
    print("Starting stock data scraping...")
    
    # Get output filename from environment variables
    output_file = os.getenv("YFINANCE_OUTPUT", "yfinancescrape.json")
    
    # Load emiten list from JSON file
    with open('emiten_list.json', 'r') as file:
        emiten_list = json.load(file)
    
    # Create a list to store all data
    all_data = []
    
    # Process each emiten
    for emiten in emiten_list:
        print(f"Processing {emiten}...")
        try:
            # Get stock data
            stock = yf.Ticker(emiten)
            data = stock.history(period="1y")
            
            # Reset index to make Date a regular column
            data.reset_index(inplace=True)
            
            # Convert Date to string format
            data["Date"] = data["Date"].apply(lambda x: x.strftime("%d/%m/%Y - %H:%M"))
            
            # Convert DataFrame to list of dictionaries
            records = json.loads(data.to_json(orient="records"))
            
            # Add emiten information to each record
            for record in records:
                record["emiten"] = emiten
                
            # Add these records to our main list
            all_data.extend(records)
            
            print(f"✅ Added {len(records)} records for {emiten}")
        except Exception as e:
            print(f"❌ Error processing {emiten}: {str(e)}")
    
    # Save all data to a single JSON file
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Successfully saved {len(all_data)} records to {output_file}")
    return len(all_data)


def ingest_to_mongodb():
    """
    Ingestion ke MongoDB
    Setelah dibuat JSON filenya, maka langkah selanjutnya adalah memasukkannya ke mongoDB
    """
    print("Starting MongoDB ingestion...")
    
    # Get environment variables
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    db_name = os.getenv("MONGODB_DATABASE_NAME")
    collection_name = os.getenv("COLLECTION_YFINANCE_DATA")
    output_file = os.getenv("YFINANCE_OUTPUT", "yfinancescrape.json")
    
    if not db_name:
        raise ValueError("Environment variable MONGODB_DATABASE_NAME is not set or is empty!")
    if not connection_string:
        raise ValueError("Environment variable MONGODB_CONNECTION_STRING is not set or is empty!")
    if not collection_name:
        raise ValueError("Environment variable COLLECTION_YFINANCE_DATA is not set or is empty!")
    
    # Start timing
    start_time = time.time()
    
    # Load data from JSON file
    print("Loading data from JSON file...")
    with open(output_file, "r") as f:
        all_data = json.load(f)
    
    print(f"Loaded {len(all_data)} records from JSON file")
    
    # Connect to MongoDB Atlas
    client = pymongo.MongoClient(connection_string, 
                                maxPoolSize=100,  # Increase connection pool
                                retryWrites=True)
    
    # Select database and collection
    db = client[db_name]  # Database name
    collection = db[collection_name]  # Collection name
    
    # Create compound index for faster lookups if it doesn't exist
    collection.create_index([("emiten", 1), ("Date", 1)], unique=True, background=True)
    
    # Get all existing emiten-date pairs in one query (much faster than multiple queries)
    print("Fetching existing records...")
    existing_records = {}
    for doc in collection.find({}, {"emiten": 1, "Date": 1, "_id": 0}):
        emiten = doc["emiten"]
        date = doc["Date"]
        if emiten not in existing_records:
            existing_records[emiten] = set()
        existing_records[emiten].add(date)
    
    print(f"Found existing records for {len(existing_records)} emitens")
    
    # Prepare bulk operations
    bulk_ops = []
    new_record_count = 0
    batch_size = 1000  # Process in batches
    
    print("Preparing bulk operations...")
    for record in all_data:
        emiten = record["emiten"]
        date = record["Date"]
        
        # Skip if this record already exists
        if emiten in existing_records and date in existing_records[emiten]:
            continue
        
        # Add to bulk operations
        bulk_ops.append(pymongo.InsertOne(record))
        new_record_count += 1
        
        # Execute batch if reached batch size
        if len(bulk_ops) >= batch_size:
            if bulk_ops:
                collection.bulk_write(bulk_ops, ordered=False)
                print(f"Inserted batch of {len(bulk_ops)} records")
                bulk_ops = []
    
    # Insert any remaining operations
    if bulk_ops:
        collection.bulk_write(bulk_ops, ordered=False)
        print(f"Inserted final batch of {len(bulk_ops)} records")
    
    elapsed_time = time.time() - start_time
    print(f"Completed MongoDB ingestion process. Inserted {new_record_count} new records in {elapsed_time:.2f} seconds")
    
    # Close MongoDB connection
    client.close()
    
    return new_record_count


def main():
    """
    Main function to execute the complete workflow
    """
    try:
        print("=== Stock Data Scraping and MongoDB Ingestion ===")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Scrape stock data
        total_records = scrape_stock_data()
        
        # Step 2: Ingest to MongoDB
        inserted_records = ingest_to_mongodb()
        
        print("\n=== Process Completed Successfully ===")
        print(f"Total records processed: {total_records}")
        print(f"New records inserted: {inserted_records}")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        logging.error(f"Main process error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('yfinance_scraping.log'),
            logging.StreamHandler()
        ]
    )
    
    main()