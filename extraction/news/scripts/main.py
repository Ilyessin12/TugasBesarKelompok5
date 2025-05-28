"""
Main script to run the news scraper and ingestion pipeline.
"""

import os
import logging
import argparse
import sys
# import time # Not used directly here
from dotenv import load_dotenv, find_dotenv

# Load environment variables from root .env
# This should be done before other project imports that might rely on env vars
load_dotenv(find_dotenv(raise_error_if_not_found=True))

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Not needed with PYTHONPATH=/app

# Corrected imports based on PYTHONPATH=/app and new structure
from src.news.scrapers.news_scraper import NewsScraper # Corrected path
from src.news.ingestion.news_ingestion import NewsIngestion # Corrected path
from src.news.utils.common_utils import ensure_dir, setup_logging # Corrected path

def run_scraper():
    """
    Run the news scraper.
    """
    logger = logging.getLogger(__name__)
    
    # Ensure cache directory exists using NEWS_OUTPUT_PREFIX
    # This ensures the directory for scraper output files exists.
    news_output_prefix_env = os.getenv("NEWS_OUTPUT_PREFIX")
    if news_output_prefix_env:
        ensure_dir(os.path.dirname(news_output_prefix_env))
        logger.info(f"Ensured directory exists: {os.path.dirname(news_output_prefix_env)}")
    else:
        # Fallback if NEWS_OUTPUT_PREFIX is not set, though it's crucial
        default_cache_dir = "/app/cache/news/"
        ensure_dir(default_cache_dir)
        logger.warning(f"NEWS_OUTPUT_PREFIX not set. Ensured default directory: {default_cache_dir}")
    
    logger.info("Starting News scraper...")
    news_scraper = NewsScraper()
    news_scraper.process_emiten_files()
    logger.info("News scraper completed.")


def run_ingestion():
    """
    Run the news ingestion process.
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Starting News ingestion...")
    news_ingestion = NewsIngestion()
    news_count = news_ingestion.ingest()
    logger.info(f"News ingestion completed. Ingested {news_count} records.")

def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="News Data Pipeline")
    parser.add_argument(
        "--mode",
        choices=["all", "scrape", "ingest"],
        default="all",
        help="Pipeline mode: 'all', 'scrape', or 'ingest' (default: all)"
    )
    return parser.parse_args()

def main():
    """
    Main function to run the data pipeline.
    """
    # load_dotenv() # Already loaded at the top of the script
    
    # Set up logging (common_utils.setup_logging will create logs in /app/cache/error_logs)
    setup_logging() 
    logger = logging.getLogger(__name__)
    
    args = parse_arguments()
    
    logger.info(f"Starting news data pipeline in mode '{args.mode}'")
    
    try:
        if args.mode == "all":
            run_scraper()
            run_ingestion()
        elif args.mode == "scrape":
            run_scraper()
        elif args.mode == "ingest":
            run_ingestion()
        
        logger.info("News data pipeline completed successfully")
    
    except Exception as e:
        logger.error(f"Error running news data pipeline: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()