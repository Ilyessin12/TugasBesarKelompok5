"""
News scraper for IQ Plus website.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from ..utils.common_utils import save_to_json, ensure_dir, retry_operation

class NewsScraper:
    """
    Class for scraping news from IQ Plus website.
    """
    
    def __init__(self):
        """
        Initialize the news scraper.
        """
        load_dotenv()
        self.chrome_url = os.getenv("CHROME_URL")
        self.selenium_timeout = int(os.getenv("SELENIUM_TIMEOUT", "30"))
        self.news_output_prefix = os.getenv("NEWS_OUTPUT_PREFIX")
        self.driver = None
        self.logger = logging.getLogger(__name__)
    
    def _initialize_driver(self):
        """
        Initialize the Selenium WebDriver.
        """
        if self.chrome_url:
            # Use remote WebDriver (Selenium container)
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Remote(
                command_executor=self.chrome_url,
                options=options
            )
        else:
            # Use local WebDriver
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        
        self.logger.info("WebDriver initialized")
    
    def scrape_news(self, emiten_list: List[str], output_file: str) -> List[Dict[str, Any]]:
        """
        Scrape news for a list of emitens.
        
        Args:
            emiten_list: List of emiten codes
            output_file: Path to output file
            
        Returns:
            List[Dict[str, Any]]: List of news items
        """
        # Dictionary to store all news data
        news_data = []
        
        try:
            # Initialize WebDriver if not already initialized
            if self.driver is None:
                self._initialize_driver()
            
            # Loop through each ticker
            for emiten in emiten_list:
                self.logger.info(f"Searching news for {emiten}...")
                
                # Open the search URL
                search_url = "http://www.iqplus.info/news/search/"
                self.driver.get(search_url)
                
                # Wait for the search input element to be present and interact with it
                try:
                    search_input = WebDriverWait(self.driver, self.selenium_timeout).until(
                        EC.presence_of_element_located((By.NAME, "search"))
                    )
                    # Interact with the search input once it's present
                    search_input.send_keys(emiten)
                    search_input.submit()
                except Exception as e:
                    self.logger.error(f"Search input element not found for {emiten}: {e}")
                    continue  # Skip to the next ticker if the search input is not found
                
                time.sleep(3)  # Wait for the page to load
                
                # Parse the page source
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                
                # Find news items
                news_list = soup.find_all("li", style="text-transform:capitalize;")
                
                # Extract news details
                if news_list:
                    self.logger.info(f"Found {len(news_list)} news items for {emiten}")
                    for news in news_list:
                        date_time = news.find("b").text.strip() if news.find("b") else "No Date"
                        title = news.find("a").text.strip() if news.find("a") else "No Title"
                        link = news.find("a")["href"] if news.find("a") else "#"
                        
                        # Check if title contains the emiten name followed by a colon
                        if f"{emiten}:" in title:
                            # Append news as a dictionary
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
            
            # Save the news data to a JSON file
            save_to_json(news_data, output_file)
            self.logger.info(f"News data saved to {output_file}")
        
        except Exception as e:
            self.logger.error(f"Error scraping news: {e}")
        
        return news_data
    
    def close(self):
        """
        Close the WebDriver.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("WebDriver closed")
    
    def __del__(self):
        """
        Destructor to ensure WebDriver is closed.
        """
        self.close()

    @retry_operation(max_retries=3, delay=5)
    def process_emiten_files(self):
        """
        Process JSON files from pt1 to pt5.
        """
        try:
            # Process JSON files from pt1 to pt5
            for i in range(1, 6):
                # Gunakan jalur absolut
                input_file = os.path.join('/app/src/scrapers', f"emiten_list_pt{i}.json")
                output_file = f"{self.news_output_prefix}{i}"
                
                try:
                    # Read emiten list from JSON file
                    with open(input_file, "r", encoding="utf-8") as file:
                        emiten_list = json.load(file)
                    self.logger.info(f"Successfully loaded {len(emiten_list)} emiten from {input_file}")
                    
                    # Scrape news for the current emiten list
                    self.scrape_news(emiten_list, output_file)
                
                except FileNotFoundError:
                    self.logger.error(f"Error: {input_file} not found. Skipping...")
                    continue
                except json.JSONDecodeError:
                    self.logger.error(f"Error: Invalid JSON format in {input_file}. Skipping...")
                    continue
        finally:
            self.close()


def main():
    """
    Main function to run the news scraper.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create cache directory
    ensure_dir(os.path.dirname(os.getenv("NEWS_OUTPUT_PREFIX", "/app/cache/news/")))
    
    # Initialize and run scraper
    scraper = NewsScraper()
    scraper.process_emiten_files()


if __name__ == "__main__":
    main() 