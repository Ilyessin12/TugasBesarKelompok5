import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import pymongo
import logging
import re

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_selenium_driver():
    """Setup and configure Chrome WebDriver with optimized settings"""
    options = Options()
    options.add_argument('--headless')  # Run in headless mode for production
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # For debugging, you can comment out headless mode
    # options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def clean_content(content):
    """Clean and format news content using regex patterns"""
    if not content:
        return ""
    
    # Remove leading numeric ID and date pattern (e.g., "11937555 , (30/4) - ")
    content = re.sub(r'^\d+\s*,\s*\([^)]+\)\s*-\s*', '', content)
    
    # Remove IQPlus prefix patterns
    content = re.sub(r'^\d+\s+IQPlus,\s*\([^)]+\)\s*-\s*', '', content)
    
    # Remove "IQPlus" occurrences
    content = re.sub(r'\bIQPlus\b', '', content)
    
    # Remove common unwanted patterns
    unwanted_patterns = [
        r'x\|\s*IQPLUS\s*NEWS',  # "x| IQPLUS NEWS"
        r'\(end/ant\)$',         # "(end/ant)" at the end
        r'\(end/[a-z]+\)$',      # Other end patterns like (end/xyz)
        r'^\d+\s+IQPlus,?\s*',   # Numeric prefix with IQPlus
    ]
    
    for pattern in unwanted_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Clean up multiple spaces and trim
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Remove leading/trailing punctuation that might be left over
    content = re.sub(r'^[,\-\s]+|[,\-\s]+$', '', content).strip()
    
    return content

def get_news_content(driver, link):
    """Get full content of news article with improved extraction methods"""
    try:
        driver.get(link)
        time.sleep(3)  # Increased wait time for page to fully load
        
        content = ""
        
        # Method 1: Try to get content from meta description (most reliable for this site)
        try:
            meta_desc = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
            if meta_desc:
                content = meta_desc.get_attribute('content')
                logger.debug(f"Content extracted via meta description: {len(content)} characters")
        except:
            pass
        
        # Method 2: Try to get content from the main content div
        if not content:
            try:
                content_div = driver.find_element(By.CLASS_NAME, 'midcol')
                if content_div:
                    content = content_div.text
                    logger.debug(f"Content extracted via midcol class: {len(content)} characters")
            except:
                pass
        
        # Method 3: Try to get content from load_news div
        if not content:
            try:
                content_div = driver.find_element(By.ID, 'load_news')
                if content_div:
                    content = content_div.text
                    logger.debug(f"Content extracted via load_news ID: {len(content)} characters")
            except:
                pass
        
        # Method 4: Try to parse with BeautifulSoup for more reliable extraction
        if not content:
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Try meta description with BeautifulSoup
                meta_tag = soup.find('meta', {'name': 'description'})
                if meta_tag and meta_tag.get('content'):
                    content = meta_tag.get('content')
                    logger.debug(f"Content extracted via BeautifulSoup meta: {len(content)} characters")
                
                # If still no content, try to find main content areas
                if not content:
                    # Try various content selectors
                    selectors = [
                        'div.midcol',
                        'div#load_news',
                        'div[style*="width:450px"]',
                        'body'
                    ]
                    
                    for selector in selectors:
                        try:
                            element = soup.select_one(selector)
                            if element and element.get_text().strip():
                                content = element.get_text().strip()
                                logger.debug(f"Content extracted via selector {selector}: {len(content)} characters")
                                break
                        except:
                            continue
            except Exception as e:
                logger.debug(f"BeautifulSoup extraction failed: {str(e)}")
        
        # Method 5: If all else fails, try to get any meaningful text from page
        if not content:
            try:
                # Get page source and try to extract meaningful content
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text and clean it
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                content = ' '.join(chunk for chunk in chunks if chunk)
                
                # If content is too long, try to find the main news content
                if len(content) > 2000:
                    # Look for content that contains typical news patterns
                    sentences = content.split('.')
                    news_content = []
                    for sentence in sentences:
                        if any(keyword in sentence.lower() for keyword in ['jakarta', 'tbk', 'perseroan', 'triliun', 'persen']):
                            news_content.append(sentence.strip())
                    
                    if news_content:
                        content = '. '.join(news_content[:10])  # Take first 10 relevant sentences
                
                logger.debug(f"Content extracted via fallback method: {len(content)} characters")
            except Exception as e:
                logger.debug(f"Fallback extraction failed: {str(e)}")
        
        # Clean and return content
        cleaned_content = clean_content(content)
        
        if cleaned_content:
            logger.info(f"Successfully extracted content ({len(cleaned_content)} characters) from {link}")
        else:
            logger.warning(f"No content could be extracted from {link}")
        
        return cleaned_content
    
    except Exception as e:
        logger.warning(f"Error getting content from {link}: {str(e)}")
        return ""

def scrape_news(emiten_list, output_file=None, get_content=True):  # Changed default to True
    """
    Scrape news for given list of emiten (stock codes)
    
    Args:
        emiten_list: List of stock codes to search
        output_file: Optional file to save results
        get_content: Whether to fetch full article content
    
    Returns:
        List of news data dictionaries
    """
    news_data = []
    driver = setup_selenium_driver()
    
    try:
        for emiten in emiten_list:
            logger.info(f"Searching news for {emiten}...")
            
            # Open the search URL
            search_url = "http://www.iqplus.info/news/search/"
            driver.get(search_url)

            # Wait for the search input element and interact with it
            try:
                search_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "search"))
                )
                search_input.clear()
                search_input.send_keys(emiten)
                search_input.submit()
            except Exception as e:
                logger.error(f"Search input element not found for {emiten}: {str(e)}")
                continue

            time.sleep(3)  # Wait for the page to load

            # Parse the page source
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Find news items
            news_list = soup.find_all("li", style="text-transform:capitalize;")

            # Extract news details
            if news_list:
                logger.info(f"Found {len(news_list)} news items for {emiten}")
                for news in news_list:
                    try:
                        date_time = news.find("b").text.strip() if news.find("b") else "No Date"
                        title = news.find("a").text.strip() if news.find("a") else "No Title"
                        link = news.find("a")["href"] if news.find("a") else "#"
                        
                        # Make sure link is absolute
                        if link.startswith("/"):
                            link = "http://www.iqplus.info" + link

                        # Check if title contains the emiten name followed by a colon
                        if f"{emiten}:" in title:
                            news_item = {
                                "Emiten": emiten,
                                "Date": date_time,
                                "Title": title,
                                "Link": link
                            }
                            
                            # Get full content if requested
                            if get_content:
                                logger.info(f"Extracting content for: {title}")
                                content = get_news_content(driver, link)
                                news_item["Content"] = content
                                
                                # Add content length for monitoring
                                news_item["Content_Length"] = len(content) if content else 0
                            
                            news_data.append(news_item)
                            logger.info(f"Added news item: {title}")
                        else:
                            logger.debug(f"Skipping news item as title does not contain '{emiten}:'")
                    
                    except Exception as e:
                        logger.error(f"Error processing news item for {emiten}: {str(e)}")
                        continue
            else:
                logger.info(f"No news found for {emiten}.")

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
    
    finally:
        driver.quit()

    # Save the news data to a JSON file if output_file is specified
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(news_data, json_file, indent=4, ensure_ascii=False)
            logger.info(f"News data saved to {output_file}")
            
            # Log summary of content extraction
            content_stats = {
                "total_items": len(news_data),
                "items_with_content": len([item for item in news_data if item.get("Content")]),
                "avg_content_length": sum(item.get("Content_Length", 0) for item in news_data) / len(news_data) if news_data else 0
            }
            logger.info(f"Content extraction summary: {content_stats}")
            
        except Exception as e:
            logger.error(f"Error saving to {output_file}: {str(e)}")
    
    return news_data

def scrape_all_news_files():
    """Process all emiten list files and scrape news"""
    news_output_prefix = os.getenv("NEWS_OUTPUT_PREFIX", "news_data_pt")
    all_scraped_data = []
    
    # Create output directory if it doesn't exist
    output_dir = "scraped_data"
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory created/verified: {output_dir}")
    
    # Process JSON files from pt1 to pt5
    for i in range(1, 6):
        input_file = f"emiten_list_pt{i}.json"
        output_file = os.path.join(output_dir, f"{news_output_prefix}{i}.json")
        
        logger.info(f"Processing {input_file} -> {output_file}")

        try:
            # Check if input file exists
            if not os.path.exists(input_file):
                logger.warning(f"Input file {input_file} not found. Skipping...")
                continue
                
            # Read emiten list from JSON file
            with open(input_file, "r", encoding="utf-8") as file:
                emiten_list = json.load(file)
            logger.info(f"Successfully loaded {len(emiten_list)} emiten from {input_file}")

            # Scrape news for the current emiten list (with content extraction enabled by default)
            scraped_data = scrape_news(emiten_list, output_file, get_content=True)
            all_scraped_data.extend(scraped_data)
            logger.info(f"Scraped {len(scraped_data)} news items from {input_file}")
            
            # Verify file was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"Output file {output_file} created successfully (size: {file_size} bytes)")
            else:
                logger.warning(f"Output file {output_file} was not created!")

        except FileNotFoundError:
            logger.error(f"Error: {input_file} not found. Skipping...")
            continue
        except json.JSONDecodeError:
            logger.error(f"Error: Invalid JSON format in {input_file}. Skipping...")
            continue
        except Exception as e:
            logger.error(f"Error processing {input_file}: {str(e)}")
            continue
    
    logger.info(f"Total scraped data: {len(all_scraped_data)} items")
    return all_scraped_data

def ingest_to_mongodb():
    """Ingest scraped news data to MongoDB"""
    # Get environment variables
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    db_name = os.getenv("MONGODB_DATABASE_NAME")
    collection_name = os.getenv("COLLECTION_NEWS")
    news_output_prefix = os.getenv("NEWS_OUTPUT_PREFIX", "news_data_pt")
    
    if not all([connection_string, db_name, collection_name]):
        logger.error("Missing MongoDB configuration in environment variables")
        return
    
    start_time = time.time()
    output_dir = "scraped_data"

    # Load data from all JSON files
    logger.info("Loading data from JSON files...")
    all_news_data = []

    for i in range(1, 6):
        file_name = os.path.join(output_dir, f"{news_output_prefix}{i}.json")
        try:
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as f:
                    news_data = json.load(f)
                    all_news_data.extend(news_data)
                    logger.info(f"Loaded {len(news_data)} records from {file_name}")
            else:
                logger.warning(f"File {file_name} not found. Skipping...")
        except json.JSONDecodeError:
            logger.warning(f"Warning: Invalid JSON format in {file_name}. Skipping...")

    if not all_news_data:
        logger.warning("No data to ingest. Please check if scraping was successful.")
        logger.info("Files should be located in 'scraped_data' directory:")
        for i in range(1, 6):
            file_path = os.path.join(output_dir, f"{news_output_prefix}{i}.json")
            exists = "✓" if os.path.exists(file_path) else "✗"
            logger.info(f"  {exists} {file_path}")
        return

    logger.info(f"Loaded total of {len(all_news_data)} news records from all files")

    try:
        # Connect to MongoDB Atlas
        client = pymongo.MongoClient(connection_string, 
                                   maxPoolSize=100,
                                   retryWrites=True)

        # Select database and collection
        db = client[db_name]
        collection = db[collection_name]

        # Create compound index for faster lookups if it doesn't exist
        collection.create_index([("Emiten", 1), ("Date", 1), ("Title", 1)], 
                              unique=True, background=True)

        # Get all existing emiten-date-title combinations in one query
        logger.info("Fetching existing records...")
        existing_records = {}
        for doc in collection.find({}, {"Emiten": 1, "Date": 1, "Title": 1, "_id": 0}):
            emiten = doc["Emiten"]
            date = doc["Date"]
            title = doc["Title"]
            
            if emiten not in existing_records:
                existing_records[emiten] = {}
            
            if date not in existing_records[emiten]:
                existing_records[emiten][date] = set()
            
            existing_records[emiten][date].add(title)

        logger.info(f"Found existing records for {len(existing_records)} emitens")

        # Prepare bulk operations
        bulk_ops = []
        new_record_count = 0
        batch_size = 1000

        logger.info("Preparing bulk operations...")
        for record in all_news_data:
            emiten = record["Emiten"]
            date = record["Date"]
            title = record["Title"]
            
            # Skip if this record already exists
            if (emiten in existing_records and 
                date in existing_records[emiten] and 
                title in existing_records[emiten][date]):
                continue
            
            # Add to bulk operations
            bulk_ops.append(pymongo.InsertOne(record))
            new_record_count += 1
            
            # Execute batch if reached batch size
            if len(bulk_ops) >= batch_size:
                if bulk_ops:
                    collection.bulk_write(bulk_ops, ordered=False)
                    logger.info(f"Inserted batch of {len(bulk_ops)} records")
                    bulk_ops = []

        # Insert any remaining operations
        if bulk_ops:
            collection.bulk_write(bulk_ops, ordered=False)
            logger.info(f"Inserted final batch of {len(bulk_ops)} records")

        elapsed_time = time.time() - start_time
        logger.info(f"Completed MongoDB ingestion process. Inserted {new_record_count} new records in {elapsed_time:.2f} seconds")
        
        client.close()
        return new_record_count

    except Exception as e:
        logger.error(f"Error during MongoDB ingestion: {str(e)}")
        return 0

def test_single_emiten(emiten_code):
    """Test scraping for a single emiten with detailed content extraction"""
    logger.info(f"Testing scraping for single emiten: {emiten_code}")
    result = scrape_news([emiten_code], get_content=True)
    
    logger.info(f"Found {len(result)} news items for {emiten_code}")
    for item in result:
        logger.info(f"- {item['Date']}: {item['Title']}")
        if item.get('Content'):
            logger.info(f"  Content length: {len(item['Content'])} characters")
            logger.info(f"  Content preview: {item['Content'][:200]}...")
        else:
            logger.warning(f"  No content extracted")
    
    return result

def test_content_cleaning():
    """Test the clean_content function with various examples"""
    test_cases = [
        "11937555 , (30/4) - PT. Astra Agro Lestari Tbk. (AALI) bakal membagika…",
        "14740419 IQPlus, (28/5) - PT Bank Rakyat Indonesia (Persero) Tbk (BRI) menyampaikan...",
        "Some content with IQPlus in the middle and x| IQPLUS NEWS at the end",
        "Normal content without unwanted patterns",
        "Content ending with (end/ant)",
        "12345 , (15/3) - Regular news content here (end/xyz)"
    ]
    
    logger.info("=== TESTING CONTENT CLEANING ===")
    for i, test_case in enumerate(test_cases, 1):
        cleaned = clean_content(test_case)
        logger.info(f"Test {i}:")
        logger.info(f"  Input:  {test_case}")
        logger.info(f"  Output: {cleaned}")
        logger.info("")

def main():
    """Main function to run the complete scraping and ingestion process"""
    logger.info("Starting news scraping and MongoDB ingestion process...")
    
    # Check if input files exist
    logger.info("Checking input files...")
    input_files_exist = False
    for i in range(1, 6):
        input_file = f"emiten_list_pt{i}.json"
        if os.path.exists(input_file):
            logger.info(f"✓ Found {input_file}")
            input_files_exist = True
        else:
            logger.warning(f"✗ Missing {input_file}")
    
    if not input_files_exist:
        logger.error("No input files found! Please ensure emiten_list_pt1.json to emiten_list_pt5.json exist")
        return
    
    try:
        # Step 1: Scrape all news data
        logger.info("Step 1: Scraping news data...")
        scraped_data = scrape_all_news_files()
        
        if not scraped_data:
            logger.warning("No data was scraped. Please check:")
            logger.warning("1. Internet connection")
            logger.warning("2. Website accessibility (http://www.iqplus.info)")
            logger.warning("3. Input file content (should contain valid emiten codes)")
            
            # Show what files were created
            output_dir = "scraped_data"
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                if files:
                    logger.info(f"Files in {output_dir}: {files}")
                else:
                    logger.info(f"Directory {output_dir} is empty")
            return
        
        logger.info(f"Successfully scraped {len(scraped_data)} news items")
        
        # Log content extraction statistics
        items_with_content = len([item for item in scraped_data if item.get("Content")])
        avg_content_length = sum(item.get("Content_Length", 0) for item in scraped_data) / len(scraped_data) if scraped_data else 0
        logger.info(f"Content extraction stats: {items_with_content}/{len(scraped_data)} items have content, avg length: {avg_content_length:.0f} chars")
        
        # Step 2: Ingest to MongoDB
        logger.info("Step 2: Ingesting data to MongoDB...")
        inserted_count = ingest_to_mongodb()
        
        if inserted_count > 0:
            logger.info(f"Successfully inserted {inserted_count} new records to MongoDB")
        else:
            logger.info("No new records to insert (all data already exists)")
        
        logger.info("Process completed successfully!")
        
        # Show final summary
        output_dir = "scraped_data"
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Scraped files location: {os.path.abspath(output_dir)}")
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            for file in files:
                file_path = os.path.join(output_dir, file)
                size = os.path.getsize(file_path)
                logger.info(f"  - {file} ({size} bytes)")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

# Additional helper function to check and debug file creation
def debug_file_paths():
    """Debug function to check file paths and permissions"""
    logger.info("=== DEBUG FILE PATHS ===")
    
    # Check current working directory
    cwd = os.getcwd()
    logger.info(f"Current working directory: {cwd}")
    
    # Check input files
    logger.info("Input files:")
    for i in range(1, 6):
        input_file = f"emiten_list_pt{i}.json"
        path = os.path.abspath(input_file)
        exists = os.path.exists(input_file)
        logger.info(f"  {input_file}: {'✓' if exists else '✗'} ({path})")
    
    # Check output directory
    output_dir = "scraped_data"
    output_path = os.path.abspath(output_dir)
    logger.info(f"Output directory: {output_path}")
    
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        logger.info(f"Files in output directory: {files}")
    else:
        logger.info("Output directory does not exist yet")
    
    # Check permissions
    try:
        test_file = "test_write.txt"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        logger.info("✓ Write permissions OK")
    except Exception as e:
        logger.error(f"✗ Write permission error: {e}")

if __name__ == "__main__":
    # For debugging file paths, uncomment the line below:
    # debug_file_paths()
    
    # For testing content cleaning function, uncomment the line below:
    # test_content_cleaning()
    
    # For testing single emiten, uncomment the line below:
    # test_single_emiten("BBRI")
    
    # Run the complete process
    main()