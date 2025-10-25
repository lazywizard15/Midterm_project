"""
Tests for app/logger.py
"""
import pytest
import logging
from pathlib import Path
from app.logger import setup_logging

# Use a mock config
class MockConfig:
    def __init__(self, tmp_path):
        self._log_dir = tmp_path / "test_logs"
        self._log_file = self._log_dir / "app.log"
        
    def get_setting(self, key, default=None):
        if key == 'CALCULATOR_LOG_DIR':
            return self._log_dir
        return default
        
    def get_log_file_path(self):
        return self._log_file

@pytest.fixture
def mock_config(tmp_path):
    """Provides a mock config that points to a temp log file."""
    (tmp_path / "test_logs").mkdir()
    return MockConfig(tmp_path)

def test_setup_logging(mock_config):
    """Tests that the logger is configured correctly."""
    # Clear any existing handlers
    logger = logging.getLogger('app')
    logger.handlers = []

    logger = setup_logging(mock_config)
    
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 2 # Console and File
    
    # Test that info messages are written to the log file
    log_file = mock_config.get_log_file_path()
    assert log_file.exists()
    
    logger.info("This is a test log message.")
    
    log_content = log_file.read_text()
    assert "This is a test log message." in log_content
    
    # Test that fallback logging works
    logger.handlers = []
    bad_config = "not a config"
    fallback_logger = setup_logging(bad_config)
    assert fallback_logger.level == logging.INFO
    fallback_logger.error("Fallback test") # Should not raise an error