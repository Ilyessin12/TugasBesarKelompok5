"""
Main script to run the news scraper and ingestion pipeline.
"""

import os
import logging
import argparse
import sys
import time
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers import NewsScraper
from src.ingestion import NewsIngestion
from src.utils.common_utils import ensure_dir, setup_logging


def run_scraper():
    """
    Run the news scraper.
    """
    logger = logging.getLogger(__name__)
    
    # Ensure cache directory exists
    ensure_dir(os.path.dirname(os.getenv("NEWS_OUTPUT_PREFIX", "/app/cache/news/")))
    
    # Run News scraper
    logger.info("Starting News scraper...")
    news_scraper = NewsScraper()
    news_scraper.process_emiten_files()
    logger.info("News scraper completed.")


def run_ingestion():
    """
    Run the news ingestion process.
    """
    logger = logging.getLogger(__name__)
    
    # Run News ingestion
    logger.info("Starting News ingestion...")
    news_ingestion = NewsIngestion()
    news_count = news_ingestion.ingest()
    logger.info(f"News ingestion completed. Ingested {news_count} records.")


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run news scraper and ingestion process")
    
    parser.add_argument(
        "--mode",
        choices=["all", "scrape", "ingest"],
        default="all",
        help="Mode to run (all, scrape, ingest)"
    )
    
    return parser.parse_args()


def main():
    """
    Main function to run the data pipeline.
    """
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info(f"Starting news data pipeline in mode '{args.mode}'")
    
    try:
        if args.mode == "all":
            # Run scraper and ingestion
            run_scraper()
            run_ingestion()
        
        elif args.mode == "scrape":
            # Run only scraper
            run_scraper()
        
        elif args.mode == "ingest":
            # Run only ingestion
            run_ingestion()
        
        logger.info("News data pipeline completed successfully")
    
    except Exception as e:
        logger.error(f"Error running news data pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 