"""
Manages loading configuration from .env files.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from app.exceptions import ConfigError

class ConfigLoader:
    """Loads and provides access to configuration settings from a .env file."""
    
    def __init__(self, dotenv_path: Path):
        if not dotenv_path.exists():
            raise ConfigError(f"Configuration file not found at: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
        # Store the project root (where .env lives)
        self._project_root = dotenv_path.parent
        
        # Ensure base directories exist
        self._setup_directories()

    def _get_path(self, var_name: str, default: str) -> Path:
        """Gets a path setting and ensures it's an absolute Path object."""
        value = os.getenv(var_name, default)
        path = Path(value)
        if not path.is_absolute():
            # Use the stored project root
            path = self._project_root / value
        return path.resolve() # Resolve to make it absolute

    def _setup_directories(self):
        """Creates log and history directories if they don't exist."""
        try:
            log_dir = self.get_setting('CALCULATOR_LOG_DIR', 'logs')
            history_dir = self.get_setting('CALCULATOR_HISTORY_DIR', 'data')
            
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            Path(history_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ConfigError(f"Failed to create directories: {e}")

    def get_setting(self, key: str, default=None):
        """
        Retrieves a setting from environment variables.
        Special handling for paths to ensure they are absolute.
        """
        if key in ('CALCULATOR_LOG_DIR', 'CALCULATOR_HISTORY_DIR'):
            return self._get_path(key, default or '.')
        
        return os.getenv(key, default)

    def get_log_file_path(self) -> Path:
        """Constructs the full path for the log file."""
        log_dir = self.get_setting('CALCULATOR_LOG_DIR', 'logs')
        return Path(log_dir) / 'app.log'

    def get_history_file_path(self) -> Path:
        """Constructs the full path for the history CSV file."""
        history_dir = self.get_setting('CALCULATOR_HISTORY_DIR', 'data')
        return Path(history_dir) / 'history.csv'