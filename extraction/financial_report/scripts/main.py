"""
Main script to run the financial report scraper.
"""

import os
import logging
import argparse
import sys
from dotenv import load_dotenv

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers import FinancialReportScraper
from src.ingestion import FinancialReportIngestion
from src.utils.common_utils import ensure_dir, setup_logging


def run_scraper():
    """
    Run the financial report scraper.
    """
    logger = logging.getLogger(__name__)
    
    # Ensure cache directories exist
    ensure_dir(os.getenv("BASE_DOWNLOAD_DIR", "/app/cache/financial_reports/downloads"))
    
    # Run Financial Report scraper
    logger.info("Starting Financial Report scraper...")
    financial_scraper = FinancialReportScraper()
    financial_reports = financial_scraper.scrape_financial_reports()
    logger.info(f"Financial Report scraper completed. Scraped {len(financial_reports)} reports.")


def run_ingestion():
    """
    Run the financial report ingestion.
    """
    logger = logging.getLogger(__name__)
    
    # Run Financial Report ingestion
    logger.info("Starting Financial Report ingestion...")
    financial_ingestion = FinancialReportIngestion()
    insert_count, update_count = financial_ingestion.ingest()
    logger.info(f"Financial Report ingestion completed. Inserted {insert_count} and updated {update_count} reports.")


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run financial report scraper and ingestion processes")
    
    parser.add_argument(
        "--mode",
        choices=["all", "scrape", "ingest"],
        default="all",
        help="Mode to run (all, scrape, ingest)"
    )
    
    return parser.parse_args()


def main():
    """
    Main function to run the financial report scraper and ingestion.
    """
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info(f"Starting financial report pipeline in mode '{args.mode}'")
    
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
        
        logger.info("Financial report pipeline completed successfully")
    
    except Exception as e:
        logger.error(f"Error running financial report pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 