"""
Configures the Python logging module for the application.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from app.calculator_config import ConfigLoader

def setup_logging(config: ConfigLoader) -> logging.Logger:
    """
    Configures and returns a logger instance.
    """
    try:
        log_file_path = config.get_log_file_path()
        
        # Use a name specific to the app module
        logger = logging.getLogger('app')
        logger.setLevel(logging.INFO) # Set base level

        # Prevent logs from propagating to the root logger
        logger.propagate = False

        # Console Handler (for errors)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)

        # File Handler (for all info-level logs and above)
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=10*1024*1024, # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)

        # Add handlers only if they haven't been added before
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        logger.info(f"Logging configured. Log file at: {log_file_path}")
        return logger
        
    except Exception as e:
        # Fallback basic logging if setup fails
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('app')
        logger.error(f"Failed to configure logging: {e}", exc_info=True)
        return logger