"""
Configuration handler for the calculator app.
Loads settings from environment or uses defaults.
"""

import os
from dotenv import load_dotenv
from app.exceptions import ConfigurationError


class CalcSettings:
    """Loads and stores all calculator settings."""

    def __init__(self):
        """Initialize and validate settings."""
        load_dotenv()

        # Directory paths
        self.logs_dir = os.getenv("CALCULATOR_LOG_DIR") or "logs"
        self.history_dir = os.getenv("CALCULATOR_HISTORY_DIR") or "history"

        # Configuration values with defaults
        self.max_history = self._get_env("CALCULATOR_MAX_HISTORY_SIZE", default=100, cast=int)
        self.precision = self._get_env("CALCULATOR_PRECISION", default=2, cast=int)
        self.max_input = self._get_env("CALCULATOR_MAX_INPUT_VALUE", default=1_000_000.0, cast=float)
        self.auto_save = self._get_env("CALCULATOR_AUTO_SAVE", default=True, cast=bool)
        self.encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING") or "utf-8"

        # Files
        self.log_file = os.getenv("CALCULATOR_LOG_FILE") or os.path.join(self.logs_dir, "calculator.log")
        self.history_file = os.getenv("CALCULATOR_HISTORY_FILE") or os.path.join(self.history_dir, "calc_history.csv")

        # Make sure directories exist
        self._ensure_dirs([self.logs_dir, self.history_dir])

    def _get_env(self, key: str, default, cast):
        """
        Fetch an environment variable and cast it to the correct type.
        Falls back to default if not found. Raises error if cast fails.
        """
        val = os.getenv(key)
        if val is None:
            return default

        try:
            if cast is bool:
                return val.strip().lower() in ("true", "1", "yes", "on")
            return cast(val)
        except ValueError:
            raise ConfigurationError(f"Invalid value for {key}: {val} (expected {cast.__name__})")

    @staticmethod
    def _ensure_dirs(dirs):
        """Create directories if they do not exist."""
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)

    def __repr__(self):
        """Readable representation for debugging."""
        return (f"CalcSettings(logs_dir='{self.logs_dir}', "
                f"history_dir='{self.history_dir}', max_history={self.max_history}, "
                f"precision={self.precision}, max_input={self.max_input}, auto_save={self.auto_save})")
