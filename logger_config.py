import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO, max_bytes=10*1024*1024, backup_count=5):
    """Set up a logger with both file and console output.
    
    Args:
        name (str): Name of the logger
        log_file (str): Path to the log file
        level (int): Logging level (default: logging.INFO)
        max_bytes (int): Maximum size of log file before rotation (default: 10MB)
        backup_count (int): Number of backup files to keep (default: 5)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    
    # Create and configure file handler with rotation
    file_handler = RotatingFileHandler(
        os.path.join('logs', log_file),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers = []
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create main loggers
check_tv_logger = setup_logger('check_tv', 'check_tv.log')
relive_tv_logger = setup_logger('relive_tv', 'relive_tv.log') 
gui_logger = setup_logger('gui', 'gui.log')
