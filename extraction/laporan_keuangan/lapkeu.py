#!/usr/bin/env python3
"""
IDX Financial Reports Scraper
Mengunduh dan memproses laporan keuangan dari IDX, kemudian menyimpan ke MongoDB
"""

# Import libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import time
import os
import zipfile
import json
import xml.etree.ElementTree as ET
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# === KONFIGURASI ===
CURRENT_DIR = os.getcwd()
BASE_DIR = os.path.join(CURRENT_DIR, os.getenv("BASE_DOWNLOAD_DIR", "downloads"))
JSON_OUTPUT_FILE = os.path.join(CURRENT_DIR, os.getenv("FINANCIAL_REPORTS_OUTPUT", "financial_reports.json"))
IDX_URL = "https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan"
EMITEN_LIST_FILE = "emiten_list.json"

# MongoDB Configuration
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", "mongodb+srv://kelompok-5:FwJP0h7Bo6cTpEol@big-data.do3of.mongodb.net/?retryWrites=true&w=majority&ssl=true")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "Big_Data_kel_5")
COLLECTION_FINANCIAL_REPORTS = os.getenv("COLLECTION_FINANCIAL_REPORTS", "Docker_Scraping_Laporan_Keuangan")

def create_directories():
    """Membuat direktori yang dibutuhkan"""
    os.makedirs(BASE_DIR, exist_ok=True)
    logger.info(f"Directory created: {BASE_DIR}")

def load_existing_reports():
    """Load data laporan yang sudah ada dari file JSON"""
    existing_reports = []
    already_scraped_companies = set()
    
    if os.path.exists(JSON_OUTPUT_FILE):
        try:
            with open(JSON_OUTPUT_FILE, 'r') as f:
                existing_reports = json.load(f)
                logger.info(f"Loaded {len(existing_reports)} existing reports from {JSON_OUTPUT_FILE}")
                already_scraped_companies = {report['company'] for report in existing_reports}
                logger.info(f"Already scraped {len(already_scraped_companies)} companies")
        except json.JSONDecodeError:
            logger.error(f"Error loading {JSON_OUTPUT_FILE}, will create a new one")
            existing_reports = []
    
    return existing_reports, already_scraped_companies

def load_company_codes():
    """Load daftar kode perusahaan dari emiten_list.json"""
    try:
        with open(EMITEN_LIST_FILE) as f:
            data = json.load(f)
            company_codes = [company_code.split(".")[0] for company_code in data]
            logger.info(f"Loaded {len(company_codes)} company codes")
            return company_codes
    except FileNotFoundError:
        logger.error(f"File {EMITEN_LIST_FILE} not found!")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error parsing {EMITEN_LIST_FILE}")
        return []

def setup_selenium_driver():
    """Configure and return a Chrome WebDriver instance using Selenium Manager"""
    try:
        BASE_DIR = os.path.join(CURRENT_DIR, os.getenv("BASE_DOWNLOAD_DIR", "downloads"))
        options = webdriver.ChromeOptions()
        
        # Enhanced headless configuration
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")  # Larger window size
        
        # Additional options to improve stability
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        # User agent to mimic a real browser
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        prefs = {
            "download.default_directory": BASE_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        # Set capabilities
        options.set_capability('goog:loggingPrefs', {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL'
        })
        
        # Initialize driver using Selenium Manager (no need to specify service)
        logger.info("Initializing Chrome WebDriver with Selenium Manager")
        driver = webdriver.Chrome(options=options)
        
        # Set page load timeout
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        logger.info("Chrome WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to setup WebDriver: {str(e)}")
        logger.error(traceback.format_exc())
        raise



def xml_to_dict(element):
    """Mengubah XML menjadi dictionary secara rekursif"""
    data = {}
    for child in element:
        tag = child.tag.split("}")[-1]  # Hapus namespace
        if len(child) > 0:
            data[tag] = xml_to_dict(child)
        else:
            data[tag] = child.text
    return data

def parse_taxonomy(xsd_path):
    """Parsing file Taxonomy (.xsd) untuk mendapatkan definisi elemen"""
    if not os.path.exists(xsd_path):
        logger.warning(f"Taxonomy file {xsd_path} not found!")
        return {}

    try:
        tree = ET.parse(xsd_path)
        root = tree.getroot()
        taxonomy_dict = {}

        for elem in root.iter():
            tag = elem.tag.split("}")[-1]  # Hapus namespace
            if "name" in elem.attrib:
                taxonomy_dict[elem.attrib["name"]] = {
                    "type": elem.attrib.get("type", "unknown"),
                    "documentation": elem.attrib.get("documentation", "No description")
                }

        logger.info(f"Successfully parsed taxonomy {xsd_path}")
        return taxonomy_dict

    except Exception as e:
        logger.error(f"Error parsing taxonomy: {e}")
        return {}

def download_and_process_company(driver, company, all_financial_reports):
    """Download dan proses data untuk satu perusahaan"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # Navigate to IDX website
        driver.get(IDX_URL)
        
        # Input kode perusahaan
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.vs__search")))
        search_box.clear()
        search_box.send_keys(company)
        time.sleep(1)

        # Pilih hasil pertama
        first_suggestion = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".vs__dropdown-option")))
        first_suggestion.click()

        # Pilih filter laporan keuangan, saham, tahun 2024, tahunan
        driver.find_element(By.ID, "FinancialStatement").click()
        driver.find_element(By.ID, "TypeSaham").click()
        driver.find_element(By.ID, "year1").click()
        driver.find_element(By.ID, "period3").click()
        driver.find_element(By.XPATH, "//button[contains(text(), 'Terapkan')]").click()

        # Tunggu tabel laporan muncul
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Cari dan download file "instance.zip"
        rows = driver.find_elements(By.TAG_NAME, "tr")
        download_found = False
        
        for row in rows:
            if "instance.zip" in row.text:
                link_element = row.find_element(By.TAG_NAME, "a")
                driver.execute_script("arguments[0].scrollIntoView();", link_element)
                driver.execute_script("arguments[0].click();", link_element)
                logger.info(f"Download started for {company}")
                download_found = True
                break
        
        if not download_found:
            logger.warning(f"No instance.zip found for {company}")
            return False

        # Tunggu beberapa detik agar download selesai
        time.sleep(5)

        # Process downloaded file
        return process_downloaded_file(company, all_financial_reports)

    except Exception as e:
        logger.error(f"Error processing {company}: {e}")
        return False

def process_downloaded_file(company, all_financial_reports):
    """Proses file yang sudah didownload"""
    try:
        # === Ekstraksi File ZIP ===
        zip_path = os.path.join(BASE_DIR, "instance.zip")
        extract_dir = os.path.join(BASE_DIR, company)
        os.makedirs(extract_dir, exist_ok=True)

        if os.path.exists(zip_path):
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
                logger.info(f"Extracted {company} instance.zip")
            except zipfile.BadZipFile:
                logger.error(f"Error: {company} instance.zip is not a valid ZIP file")
                return False
            finally:
                os.remove(zip_path)  # Hapus ZIP setelah ekstraksi

        # === Parsing Taxonomy ===
        xsd_path = os.path.join(extract_dir, "taxonomy.xsd")
        taxonomy_dict = parse_taxonomy(xsd_path)

        # === Konversi XBRL ke JSON & Simpan ke Dictionary ===
        xbrl_path = os.path.join(extract_dir, "instance.xbrl")

        if os.path.exists(xbrl_path):
            try:
                tree = ET.parse(xbrl_path)
                root = tree.getroot()
                xbrl_dict = xml_to_dict(root)

                # Gabungkan XBRL dengan Taxonomy
                enriched_data = {
                    "company": company,
                    "timestamp": datetime.now().isoformat(),
                    "taxonomy": taxonomy_dict,
                    "xbrl_data": xbrl_dict
                }

                # Add to our collection of all data
                all_financial_reports.append(enriched_data)
                logger.info(f"{company} data added to collection!")
                return True

            except Exception as e:
                logger.error(f"Error processing {company}.xbrl: {e}")
                return False
        else:
            logger.error(f"instance.xbrl not found for {company}")
            return False

    except Exception as e:
        logger.error(f"Error processing downloaded file for {company}: {e}")
        return False

def save_progress(all_financial_reports):
    """Simpan progress ke file JSON"""
    try:
        with open(JSON_OUTPUT_FILE, 'w') as f:
            json.dump(all_financial_reports, f, indent=2)
        logger.info(f"Saved {len(all_financial_reports)} reports to {JSON_OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Error saving progress: {e}")

def scrape_financial_reports():
    """Main function untuk scraping laporan keuangan"""
    logger.info("Starting IDX Financial Reports Scraper...")
    
    # Setup
    create_directories()
    existing_reports, already_scraped_companies = load_existing_reports()
    company_codes = load_company_codes()
    
    if not company_codes:
        logger.error("No company codes found. Exiting.")
        return
    
    # Filter companies to scrape
    companies_to_scrape = [company for company in company_codes if company not in already_scraped_companies]
    logger.info(f"Will scrape {len(companies_to_scrape)} remaining companies out of {len(company_codes)} total")
    
    if not companies_to_scrape:
        logger.info("All companies already scraped!")
        return existing_reports
    
    # Initialize data with existing reports
    all_financial_reports = existing_reports
    
    # Setup Selenium
    driver = setup_selenium_driver()
    
    try:
        # Process each company
        for i, company in enumerate(companies_to_scrape, 1):
            logger.info(f"Processing {company} ({i}/{len(companies_to_scrape)})")
            
            success = download_and_process_company(driver, company, all_financial_reports)
            
            # Save progress every 5 companies or after any error
            if len(all_financial_reports) % 5 == 0 or not success:
                save_progress(all_financial_reports)
                logger.info(f"Interim save: {len(all_financial_reports)} reports saved")
            
            # Small delay between companies
            time.sleep(2)
    
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {e}")
    finally:
        # Final save and cleanup
        save_progress(all_financial_reports)
        driver.quit()
        logger.info("Browser closed.")
    
    return all_financial_reports

def ingest_to_mongodb(all_financial_reports):
    """Ingest data ke MongoDB"""
    if not MONGODB_CONNECTION_STRING:
        logger.error("MongoDB connection string not found in environment variables")
        return
    
    if not all_financial_reports:
        logger.info("No data to ingest to MongoDB.")
        return
    
    start_time = time.time()
    logger.info("Starting MongoDB ingestion...")
    
    try:
        # Connect to MongoDB Atlas
        client = pymongo.MongoClient(
            MONGODB_CONNECTION_STRING, 
            maxPoolSize=100,
            retryWrites=True
        )
        
        # Select database and collection
        db = client[MONGODB_DATABASE_NAME]
        collection = db[COLLECTION_FINANCIAL_REPORTS]
        
        # Create index for faster lookups
        collection.create_index([("company", 1)], unique=True, background=True)
        
        # Get existing companies
        logger.info("Fetching existing records...")
        existing_companies = set()
        for doc in collection.find({}, {"company": 1, "_id": 0}):
            existing_companies.add(doc["company"])
        
        logger.info(f"Found existing records for {len(existing_companies)} companies")
        
        # Prepare bulk operations
        bulk_ops = []
        new_record_count = 0
        update_count = 0
        batch_size = 20
        
        logger.info("Preparing bulk operations...")
        for record in all_financial_reports:
            company = record["company"]
            
            if company in existing_companies:
                # Update existing record
                bulk_ops.append(
                    pymongo.UpdateOne(
                        {"company": company},
                        {"$set": record}
                    )
                )
                update_count += 1
            else:
                # Insert new record
                bulk_ops.append(pymongo.InsertOne(record))
                new_record_count += 1
                existing_companies.add(company)
            
            # Execute batch if reached batch size
            if len(bulk_ops) >= batch_size:
                result = collection.bulk_write(bulk_ops, ordered=False)
                logger.info(f"Processed batch: {result.inserted_count} inserted, {result.modified_count} modified")
                bulk_ops = []
        
        # Process remaining operations
        if bulk_ops:
            result = collection.bulk_write(bulk_ops, ordered=False)
            logger.info(f"Processed final batch: {result.inserted_count} inserted, {result.modified_count} modified")
        
        elapsed_time = time.time() - start_time
        logger.info(f"MongoDB ingestion completed. Inserted {new_record_count} new records and updated {update_count} records in {elapsed_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error during MongoDB ingestion: {e}")
    finally:
        try:
            client.close()
        except:
            pass

def main():
    """Main function"""
    logger.info("=== IDX Financial Reports Scraper Started ===")
    
    try:
        # Scrape financial reports
        all_financial_reports = scrape_financial_reports()
        
        # Ingest to MongoDB if data exists
        if all_financial_reports:
            ingest_to_mongodb(all_financial_reports)
        
        logger.info("=== Process Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())