"""
Utility functions for the financial report scraper.
"""

import os
import json
import logging
import shutil
from typing import Dict, Any, List
from datetime import datetime
import time
from functools import wraps

def ensure_dir(directory: str) -> None:
    """
    Ensure directory exists.
    
    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Created directory: {directory}")

def save_to_json(data: List[Dict[str, Any]], file_path: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: List of data to save
        file_path: Path to the output file
    """
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logging.info(f"Saved data to {file_path}")

def load_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Data loaded from the JSON file
    """
    if not os.path.exists(file_path):
        logging.warning(f"JSON file not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in {file_path}")
        return []

def clean_cache(directory: str, exclude: List[str] = None) -> None:
    """
    Clean up cache directory.
    
    Args:
        directory: Directory to clean
        exclude: List of file names to exclude from cleaning
    """
    exclude = exclude or [".gitkeep"]
    
    if not os.path.exists(directory):
        return
    
    for item in os.listdir(directory):
        if item in exclude:
            continue
        
        item_path = os.path.join(directory, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logging.info(f"Removed directory: {item_path}")
            elif os.path.isfile(item_path):
                os.remove(item_path)
                logging.info(f"Removed file: {item_path}")
        except Exception as e:
            logging.error(f"Error cleaning {item_path}: {e}")

def retry_operation(max_retries: int = 3, delay: int = 5):
    """
    Retry decorator for operations that might fail.
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logging.warning(f"Retry {retry + 1}/{max_retries} failed: {e}")
                    if retry < max_retries - 1:
                        logging.info(f"Waiting {delay} seconds before retrying...")
                        time.sleep(delay)
            
            logging.error(f"All {max_retries} retries failed. Last error: {last_exception}")
            raise last_exception
        
        return wrapper
    
    return decorator

def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), "cache", "error_logs")
    ensure_dir(log_dir)
    
    # Log file with timestamp
    log_file = os.path.join(log_dir, f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Logging initialized. Log file: {log_file}") 