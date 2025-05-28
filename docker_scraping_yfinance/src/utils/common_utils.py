"""
Common utility functions for the application.
"""

import os
import json
import logging
import time
from functools import wraps
from typing import Any, Callable

def ensure_dir(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def save_to_json(data: Any, filename: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filename: Output filename
    """
    # Ensure directory exists
    ensure_dir(os.path.dirname(filename))
    
    # Save data to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def setup_logging() -> None:
    """
    Set up logging configuration.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create a dictionary mapping log level names to their numeric values
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Set the log level based on the environment variable, defaulting to INFO if not recognized
    numeric_level = log_levels.get(log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=log_format
    )

def retry_operation(max_retries: int = 3, delay: int = 2) -> Callable:
    """
    Decorator to retry an operation with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Base delay in seconds between retries (will be exponentially increased)
    
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed with error: {str(e)}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
            
            # If we get here, all attempts failed
            raise last_exception
        
        return wrapper
    
    return decorator 