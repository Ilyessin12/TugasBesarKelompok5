import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Path to the .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}. Trying other locations.")
    # Fallback to original logic if root .env is not found
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')  # Adjust path if .env is elsewhere
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        # Try loading from the project root if not found adjacent to config
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        else:
            print("Warning: .env file not found in any of the specified locations.")


MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
MONGODB_DATABASE_NAME = os.getenv('MONGODB_DATABASE_NAME')
COLLECTION_YFINANCE_DATA = os.getenv('COLLECTION_YFINANCE_DATA')
COLLECTION_NEWS_DATA = os.getenv('COLLECTION_NEWS_DATA', 'news')
COLLECTION_NEWS_SUMMARY_DATA = os.getenv('COLLECTION_NEWS_SUMMARY_DATA', 'news_summary')
COLLECTION_FINANCIAL_REPORTS = os.getenv('COLLECTION_FINANCIAL_REPORTS', 'financial_reports')

if not all([MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME, COLLECTION_YFINANCE_DATA]):
    print("Warning: One or more required MongoDB environment variables are not set.")
