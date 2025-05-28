from dotenv import load_dotenv
from financialreport_transformer import transform_financial_reports
from news_transformer import transform_news

def main():
    load_dotenv()
    print("Starting transformations...")
    
    try:
        transform_financial_reports()
        print("Financial report transformation completed.")
    except Exception as e:
        print(f"Error in financial report transformation: {e}")
    
    try:
        transform_news()
        print("News transformation completed.")
    except Exception as e:
        print(f"Error in news transformation: {e}")
    
    print("All transformations attempted.")

if __name__ == "__main__":
    main()