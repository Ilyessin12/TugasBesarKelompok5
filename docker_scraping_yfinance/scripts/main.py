"""
Script utama untuk menjalankan YFinance scraper dan ingestion ke MongoDB.
"""

import os
import logging
import argparse
import sys
from dotenv import load_dotenv

# Tambahkan parent directory ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers import YFinanceScraper
from src.ingestion import YFinanceIngestion
from src.utils.common_utils import ensure_dir, setup_logging


def run_scraper():
    """
    Jalankan YFinance scraper.
    """
    logger = logging.getLogger(__name__)
    
    # Pastikan direktori cache ada
    yfinance_output = os.getenv("YFINANCE_OUTPUT", "/app/cache/yfinance/stock_data.json")
    ensure_dir(os.path.dirname(yfinance_output))
    
    # Jalankan YFinance scraper
    logger.info("Memulai YFinance scraper...")
    yfinance_scraper = YFinanceScraper()
    yfinance_data = yfinance_scraper.run()
    logger.info(f"YFinance scraper selesai. Berhasil scrape {len(yfinance_data)} records.")


def run_ingestion():
    """
    Jalankan YFinance ingestion ke MongoDB.
    """
    logger = logging.getLogger(__name__)
    
    # Jalankan YFinance ingestion
    logger.info("Memulai YFinance ingestion ke MongoDB...")
    try:
        yfinance_ingestion = YFinanceIngestion()
        inserted, updated = yfinance_ingestion.ingest()
        logger.info(f"YFinance ingestion selesai. Inserted {inserted} dan updated {updated} records.")
    except ValueError as e:
        logger.error(f"Error konfigurasi MongoDB: {str(e)}")
    except Exception as e:
        logger.error(f"Error saat menjalankan YFinance ingestion: {str(e)}")


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Jalankan YFinance scraper dan ingestion")
    
    parser.add_argument(
        "--mode",
        choices=["all", "scrape", "ingest"],
        default="all",
        help="Mode yang dijalankan (all, scrape, ingest)"
    )
    
    return parser.parse_args()


def main():
    """
    Main function untuk menjalankan scraper dan ingestion.
    """
    # Load environment variables
    load_dotenv()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info(f"Memulai YFinance pipeline dalam mode '{args.mode}'")
    
    try:
        if args.mode == "all":
            # Jalankan scraper dan ingestion
            run_scraper()
            run_ingestion()
        
        elif args.mode == "scrape":
            # Hanya jalankan scraper
            run_scraper()
        
        elif args.mode == "ingest":
            # Hanya jalankan ingestion
            run_ingestion()
        
        logger.info("YFinance pipeline selesai dengan sukses")
    
    except Exception as e:
        logger.error(f"Error saat menjalankan YFinance pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 