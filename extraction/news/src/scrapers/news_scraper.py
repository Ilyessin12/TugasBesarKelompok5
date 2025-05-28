"""
News scraper for IQ Plus website.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service # Not used if using remote or ChromeDriverManager directly
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

from src.news.utils.common_utils import save_to_json, ensure_dir, retry_operation # ensure_dir might be used by main

# Load environment variables
load_dotenv(find_dotenv(raise_error_if_not_found=True))

class NewsScraper:
    """
    Class for scraping news from IQ Plus website.
    """
    
    def __init__(self):
        """
        Initialize the news scraper.
        """
        # load_dotenv() # Already loaded at module level
        self.chrome_url = os.getenv("CHROME_URL")
        self.selenium_timeout = int(os.getenv("SELENIUM_TIMEOUT", "30"))
        # NEWS_OUTPUT_PREFIX should be like /app/cache/news/news_data_
        self.news_output_prefix = os.getenv("NEWS_OUTPUT_PREFIX")
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def _initialize_driver(self):
        """
        Initialize the Selenium WebDriver.
        """
        if self.chrome_url:
            from selenium.webdriver.chrome.options import Options as ChromeOptions # Alias to avoid conflict
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Remote(
                command_executor=self.chrome_url,
                options=options
            )
        else:
            # For local WebDriver, ensure chromedriver is managed or in PATH
            # Using webdriver_manager for local setup:
            from selenium.webdriver.chrome.service import Service as ChromeService
            options = webdriver.ChromeOptions()
            options.add_argument("--headless") # Optional for local, but good for consistency
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        self.logger.info("WebDriver initialized")

    def scrape_news(self, emiten_list: List[str], output_file_path: str) -> List[Dict[str, Any]]:
        """
        Scrape news for a list of emitens.
        
        Args:
            emiten_list: List of emiten codes
            output_file_path: Path to output file (e.g., /app/cache/news/news_data_1)
            
        Returns:
            List[Dict[str, Any]]: List of news items
        """
        news_data = []
        
        try:
            if self.driver is None:
                self._initialize_driver()
            
            for emiten in emiten_list:
                self.logger.info(f"Searching news for {emiten}...")
                search_url = "http://www.iqplus.info/news/search/"
                self.driver.get(search_url)
                
                try:
                    search_input = WebDriverWait(self.driver, self.selenium_timeout).until(
                        EC.presence_of_element_located((By.NAME, "search"))
                    )
                    search_input.send_keys(emiten)
                    search_input.submit()
                except Exception as e:
                    self.logger.error(f"Search input element not found for {emiten}: {e}")
                    continue 
                
                time.sleep(3) 
                
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                news_list_items = soup.find_all("li", style="text-transform:capitalize;") # Renamed variable
                
                if news_list_items:
                    self.logger.info(f"Found {len(news_list_items)} news items for {emiten}")
                    for news_item in news_list_items: # Renamed variable
                        date_time = news_item.find("b").text.strip() if news_item.find("b") else "No Date"
                        title = news_item.find("a").text.strip() if news_item.find("a") else "No Title"
                        link = news_item.find("a")["href"] if news_item.find("a") else "#"
                        
                        if f"{emiten}:" in title:
                            news_data.append({
                                "Emiten": emiten,
                                "Date": date_time,
                                "Title": title,
                                "Link": link
                            })
                        else:
                            self.logger.debug(f"Skipping news item as title does not contain '{emiten}:'")
                else:
                    self.logger.info(f"No news found for {emiten}.")
            
            save_to_json(news_data, output_file_path) # Use the full path
            self.logger.info(f"News data saved to {output_file_path}")
        
        except Exception as e:
            self.logger.error(f"Error scraping news: {e}")
        
        return news_data

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("WebDriver closed")
    
    def __del__(self):
        self.close()

    @retry_operation(max_retries=3, delay=5)
    def process_emiten_files(self):
        """
        Process JSON files for emiten lists and scrape news.
        """
        if not self.news_output_prefix:
            self.logger.error("NEWS_OUTPUT_PREFIX is not set. Cannot determine output file paths.")
            return

        try:
            for i in range(1, 6): # Assuming emiten_list_pt1.json to emiten_list_pt5.json
                # Path to emiten list files inside the container
                input_file = os.path.join('/app/src/news/scrapers', f"emiten_list_pt{i}.json")
                # Output file will be like /app/cache/news/news_data_1
                output_file_path = f"{self.news_output_prefix}{i}"
                
                try:
                    with open(input_file, "r", encoding="utf-8") as file:
                        emiten_list_data = json.load(file) # Renamed variable
                    self.logger.info(f"Successfully loaded {len(emiten_list_data)} emiten from {input_file}")
                    
                    self.scrape_news(emiten_list_data, output_file_path)
                
                except FileNotFoundError:
                    self.logger.error(f"Error: {input_file} not found. Skipping...")
                    continue
                except json.JSONDecodeError:
                    self.logger.error(f"Error: Invalid JSON format in {input_file}. Skipping...")
                    continue
        finally:
            self.close()

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ensure cache directory exists based on NEWS_OUTPUT_PREFIX
    # Example: if NEWS_OUTPUT_PREFIX is /app/cache/news/my_news_
    # then os.path.dirname will give /app/cache/news
    news_output_prefix_env = os.getenv("NEWS_OUTPUT_PREFIX")
    if news_output_prefix_env:
        ensure_dir(os.path.dirname(news_output_prefix_env))
    else:
        # Fallback or default if not set, though it should be for scraper to work
        ensure_dir("/app/cache/news/") 
        logging.warning("NEWS_OUTPUT_PREFIX not set, using default /app/cache/news/ for ensure_dir.")

    scraper = NewsScraper()
    scraper.process_emiten_files()

if __name__ == "__main__":
    main()