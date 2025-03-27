import logging
import os
from datetime import datetime

def setup_logger():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Configure logging
    log_file = f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create logger
    logger = logging.getLogger('AllEventInOne')
    return logger

def log_event(logger, event_type, message, details=None):
    """Log an event with optional details"""
    if details:
        logger.info(f"{event_type}: {message} - Details: {details}")
    else:
        logger.info(f"{event_type}: {message}")

def log_error(logger, message, error):
    """Log an error with exception details"""
    logger.error(f"{message}: {str(error)}", exc_info=True)

def log_warning(logger, message):
    """Log a warning message"""
    logger.warning(message)

def log_info(logger, message):
    """Log an informational message"""
    logger.info(message) 