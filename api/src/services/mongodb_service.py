from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pandas as pd
from datetime import datetime, timedelta
from src.config import settings  # Assuming config is in the root or accessible path

client = None
db = None
stock_collection = None
news_collection = None
news_summary_collection = None
financial_report_collection = None

def connect_db():
    """Establishes connection to MongoDB."""
    global client, db, stock_collection, news_collection, news_summary_collection, financial_report_collection
    if client:
        return  # Already connected

    if not settings.MONGODB_CONNECTION_STRING or not settings.MONGODB_DATABASE_NAME:
        print("Error: MongoDB connection details not configured in .env")
        return

    try:
        client = MongoClient(settings.MONGODB_CONNECTION_STRING)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        db = client[settings.MONGODB_DATABASE_NAME]
        
        # Initialize all collections
        stock_collection = db[settings.COLLECTION_YFINANCE_DATA]
        news_collection = db[settings.COLLECTION_NEWS_DATA]
        news_summary_collection = db[settings.COLLECTION_NEWS_SUMMARY_DATA]
        financial_report_collection = db[settings.COLLECTION_FINANCIAL_REPORTS]  # Changed from COLLECTION_FINANCIAL_REPORT_DATA
        
        print("Successfully connected to MongoDB.")
    except ConnectionFailure as e:
        client = None
        db = None
        stock_collection = None
        news_collection = None
        news_summary_collection = None
        financial_report_collection = None
        print(f"Error connecting to MongoDB: {e}")
    except Exception as e:
        client = None
        db = None
        stock_collection = None
        news_collection = None
        news_summary_collection = None
        financial_report_collection = None
        print(f"An unexpected error occurred during MongoDB connection: {e}")


def get_stock_data(emiten, period='all'):
    """
    Fetches and aggregates stock data for a given emiten and period.

    Args:
        emiten (str): The stock ticker symbol (e.g., 'AALI.JK').
        period (str): Aggregation period ('daily', 'monthly', 'yearly', '1y', '3y', '5y', 'all').

    Returns:
        list: A list of dictionaries containing the aggregated stock data, or None if error.
    """
    if stock_collection is None:
        print("Error: Not connected to MongoDB collection.")
        # Attempt to reconnect if not connected
        connect_db()
        if stock_collection is None:
            print("Error: Reconnection attempt failed.")
            return None

    try:
        # Initial query to filter by emiten
        query = {"emiten": emiten}

        # --- Date Filtering based on period ---
        now = datetime.now()
        start_date = None

        if period == '1y':
            start_date = now - timedelta(days=365)
        elif period == '3y':
            start_date = now - timedelta(days=3*365)
        elif period == '5y':
            start_date = now - timedelta(days=5*365)
        # Add more specific date ranges if needed for 'daily', 'monthly', 'yearly' if 'all' isn't sufficient

        # Fetch all relevant data first
        # Need to parse the 'Date' string into datetime objects for filtering and aggregation
        cursor = stock_collection.find(query)
        data = list(cursor)

        if not data:
            return []  # No data found for this emiten

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)

        # --- Data Cleaning and Conversion ---
        # Handle potential errors during date parsing
        def parse_date(date_str):
            try:
                # Assuming format "DD/MM/YYYY - HH:MM"
                return pd.to_datetime(date_str, format='%d/%m/%Y - %H:%M', errors='coerce')
            except ValueError:
                try:
                    # Try parsing just the date part if time is missing or format varies
                    return pd.to_datetime(date_str.split(' - ')[0], format='%d/%m/%Y', errors='coerce')
                except Exception:
                     return pd.NaT  # Return Not a Time for unparseable formats

        df['Date'] = df['Date'].apply(parse_date)
        df = df.dropna(subset=['Date'])  # Remove rows where date couldn't be parsed

        # Convert numeric columns, coercing errors to NaN
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
             if col in df.columns:
                # Clean data: remove commas and convert
                if df[col].dtype == 'object':  # Check if the column is of object type (likely string)
                    df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=numeric_cols)  # Remove rows with non-numeric data in key fields
        df = df.sort_values(by='Date')
        df = df.set_index('Date')

        # --- Filtering based on period ---
        if start_date:
             # Ensure the index is timezone-naive or consistent with start_date
             if df.index.tz is not None:
                 start_date = start_date.tz_localize(df.index.tz)  # Adjust timezone if necessary
             else:
                 # Assuming start_date is naive UTC or local time matching the index
                 pass
             df = df[df.index >= start_date]

        if df.empty:
            return []

        # --- Aggregation ---
        agg_df = None
        if period == 'weekly':
            # Resample to weekly frequency. Use 'W' for week end or 'W-MON' for week start on Monday.
            agg_df = df.resample('W').agg(
                Open=('Open', 'first'),
                High=('High', 'max'),
                Low=('Low', 'min'),
                Close=('Close', 'last'),
                Volume=('Volume', 'sum')
            )
        elif period == 'monthly':
            # Resample to monthly frequency. Use 'M' for month end or 'MS' for month start.
            agg_df = df.resample('M').agg(
                Open=('Open', 'first'),
                High=('High', 'max'),
                Low=('Low', 'min'),
                Close=('Close', 'last'),
                Volume=('Volume', 'sum')
            )
        elif period == 'quarterly':  # Added quarterly aggregation
        # Resample to quarterly frequency. Use 'Q' for quarter end or 'QS' for quarter start.
            agg_df = df.resample('Q').agg(
                Open=('Open', 'first'),
                High=('High', 'max'),
                Low=('Low', 'min'),
                Close=('Close', 'last'),
                Volume=('Volume', 'sum')
        )
        elif period == 'yearly':
            # Resample to yearly frequency. Use 'Y' for year end or 'YS' for year start.
            agg_df = df.resample('Y').agg(
                Open=('Open', 'first'),
                High=('High', 'max'),
                Low=('Low', 'min'),
                Close=('Close', 'last'),
                Volume=('Volume', 'sum')
            )
        else:  # daily, 1y, 3y, 5y, all (no aggregation needed beyond initial fetch/filter)
            agg_df = df[['Open', 'High', 'Low', 'Close', 'Volume']]  # Select relevant columns

        if agg_df is None or agg_df.empty:
            return []

        # --- Formatting Output ---
        agg_df = agg_df.reset_index()
        # Format Date back to string if needed, or keep as datetime object depending on frontend needs
        # Example: agg_df['Date'] = agg_df['Date'].dt.strftime('%Y-%m-%d')
        agg_df['Date'] = agg_df['Date'].dt.strftime('%d/%m/%Y')  # Format as DD/MM/YYYY

        # Add emiten back
        agg_df['emiten'] = emiten

        # Replace NaN with None for JSON compatibility BEFORE converting to dict
        agg_df = agg_df.astype(object).where(pd.notnull(agg_df), None)

        # Convert DataFrame back to list of dictionaries
        result = agg_df.to_dict('records')
        return result

    except Exception as e:
        print(f"Error fetching/aggregating data for {emiten} (period: {period}): {e}")
        import traceback
        traceback.print_exc()  # Print detailed traceback for debugging
        return None


def get_news_data(emiten, limit=20, skip=0):
    """
    Fetches news data for a given emiten.
    
    Args:
        emiten (str): The stock ticker symbol (e.g., 'AALI').
        limit (int): Maximum number of news items to return.
        skip (int): Number of news items to skip (for pagination).
        
    Returns:
        list: A list of dictionaries containing news data, or None if error.
    """
    if news_collection is None:
        print("Error: Not connected to MongoDB news collection.")
        connect_db()
        if news_collection is None:
            print("Error: Reconnection attempt failed.")
            return None
            
    try:
        # Query for the specific emiten
        query = {"Emiten": emiten}
        
        # Sort by date in descending order (newest first)
        cursor = news_collection.find(query).sort("Date", -1).skip(skip).limit(limit)
        
        # Convert to list and return
        news_data = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for item in news_data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
                
        return news_data
        
    except Exception as e:
        print(f"Error fetching news data for {emiten}: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_news_summary_data(emiten, limit=20, skip=0):
    """
    Fetches summarized news data for a given emiten.
    
    Args:
        emiten (str): The stock ticker symbol (e.g., 'AALI').
        limit (int): Maximum number of news items to return.
        skip (int): Number of news items to skip (for pagination).
        
    Returns:
        list: A list of dictionaries containing summarized news data, or None if error.
    """
    if news_summary_collection is None:
        print("Error: Not connected to MongoDB news summary collection.")
        connect_db()
        if news_summary_collection is None:
            print("Error: Reconnection attempt failed.")
            return None
            
    try:
        # Query for the specific emiten
        query = {"Emiten": emiten}
        
        # Sort by date in descending order (newest first)
        cursor = news_summary_collection.find(query).sort("Date", -1).skip(skip).limit(limit)
        
        # Convert to list and return
        news_summary_data = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for item in news_summary_data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
                
        return news_summary_data
        
    except Exception as e:
        print(f"Error fetching news summary data for {emiten}: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_financial_report_data(emiten):
    """
    Fetches financial report data for a given emiten.
    
    Args:
        emiten (str): The stock ticker symbol (e.g., 'AALI').
        
    Returns:
        dict: A dictionary containing financial report data, or None if error.
    """
    if financial_report_collection is None:
        print("Error: Not connected to MongoDB financial report collection.")
        connect_db()
        if financial_report_collection is None:
            print("Error: Reconnection attempt failed.")
            return None
            
    try:
        # Query for the specific emiten
        query = {"EntityCode": emiten}
        
        # Get the most recent financial report
        financial_report = financial_report_collection.find_one(query, sort=[("_id", -1)])
        
        if not financial_report:
            return None
            
        # Convert ObjectId to string for JSON serialization
        if '_id' in financial_report:
            financial_report['_id'] = str(financial_report['_id'])
            
        return financial_report
        
    except Exception as e:
        print(f"Error fetching financial report data for {emiten}: {e}")
        import traceback
        traceback.print_exc()
        return None

# Call connect_db when the module is loaded
connect_db()
