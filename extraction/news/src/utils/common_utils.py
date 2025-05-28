"""
Common utility functions for the scraper and ingestion modules.
"""

import os
import json
import time
import logging
import functools
import shutil
from typing import Any, List, Dict, Callable, TypeVar

# Type variables for return type
T = TypeVar('T')

# Logger
logger = logging.getLogger(__name__)

def ensure_dir(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def save_to_json(data: Any, file_path: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save to
    """
    # Ensure directory exists
    ensure_dir(os.path.dirname(file_path))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_from_json(file_path: str) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to load from
        
    Returns:
        Data from the file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def clean_cache(directory: str, exclude: List[str] = None) -> None:
    """
    Clean cache files in a directory.
    
    Args:
        directory: Directory path to clean
        exclude: List of file/directory names to exclude
    """
    exclude = exclude or []
    
    if not os.path.exists(directory):
        logger.warning(f"Cache directory does not exist: {directory}")
        return
    
    for item in os.listdir(directory):
        if item in exclude:
            continue
        
        item_path = os.path.join(directory, item)
        
        try:
            if os.path.isfile(item_path):
                os.unlink(item_path)
                logger.debug(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.debug(f"Removed directory: {item_path}")
        except Exception as e:
            logger.error(f"Error cleaning cache item {item_path}: {e}")
    
    logger.info(f"Cleaned cache directory: {directory}")


def retry_operation(max_retries: int = 3, delay: int = 5):
    """
    Decorator for retrying operations that might fail.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error("Maximum retry attempts reached")
                        raise
        
        return wrapper
    
    return decorator


def setup_logging(level: int = logging.INFO, 
                  log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
    """
    Set up logging with the specified level and format.
    
    Args:
        level: Logging level
        log_format: Logging format
    """
    logging.basicConfig(
        level=level,
        format=log_format
    ) 