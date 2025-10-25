"""
Tests for app/calculator_config.py
"""
import pytest
import os
from pathlib import Path
from app.calculator_config import ConfigLoader
from app.exceptions import ConfigError

@pytest.fixture
def temp_env_setup(tmp_path):
    """
    Creates a temporary directory, a fake .env file,
    and the log/history directories within it.
    """
    # Create a fake project root
    project_root = tmp_path / "fake_project"
    project_root.mkdir()
    
    # Define paths for test logs and data relative to the fake root
    log_dir = "test_logs"
    history_dir = "test_data"
    
    # Create the fake .env file
    env_content = f"""
CALCULATOR_LOG_DIR="{log_dir}"
CALCULATOR_HISTORY_DIR="{history_dir}"

"""
    env_file = project_root / ".env"
    env_file.write_text(env_content)
    
    return {
        "project_root": project_root,
        "env_file": env_file,
        "log_dir_name": log_dir,
        "history_dir_name": history_dir
    }

def test_config_loader_success(temp_env_setup):
    """Tests successful loading of configuration and directory creation."""
    env_file = temp_env_setup["env_file"]
    project_root = temp_env_setup["project_root"]
    log_dir_name = temp_env_setup["log_dir_name"]
    history_dir_name = temp_env_setup["history_dir_name"]

    # --- 1. Test Initialization ---
    config = ConfigLoader(dotenv_path=env_file)
        
    # --- 2. Test Directory Creation ---
    # Get the paths *after* ConfigLoader has created them
    log_dir_path = config.get_setting('CALCULATOR_LOG_DIR')
    history_dir_path = config.get_setting('CALCULATOR_HISTORY_DIR')
    
    # Assert that the directories now exist
    assert log_dir_path.exists()
    assert log_dir_path.is_dir()
    assert history_dir_path.exists()
    assert history_dir_path.is_dir()

    # --- 3. Test Get Settings ---
    assert config.get_setting('CALCULATOR_MAX_HISTORY_SIZE') == "10"
    assert config.get_setting('CALCULATOR_AUTO_SAVE') == "false"
    assert config.get_setting('CALCULATOR_PRECISION') == "4"
    assert config.get_setting('CALCULATOR_MAX_INPUT_VALUE') == "1000"
    assert config.get_setting('CALCULATOR_DEFAULT_ENCODING') == 'utf-8'
        
    # Test default value fallback
    assert config.get_setting('NON_EXISTENT_KEY', 'default_val') == 'default_val'

    # --- 4. Test Path Getters ---
    # Use the paths obtained from config for comparison
    assert config.get_log_file_path() == log_dir_path / "app.log"
    assert config.get_history_file_path() == history_dir_path / "history.csv"



def test_config_loader_file_not_found(tmp_path):
    """Tests that ConfigError is raised if the .env file is missing."""
    missing_env = tmp_path / "non_existent.env"
    
    with pytest.raises(ConfigError, match="Configuration file not found"):
        ConfigLoader(dotenv_path=missing_env)

def test_config_loader_directory_creation_fails(temp_env_setup, monkeypatch):
    """Tests that ConfigError is raised if directory creation fails."""
    env_file = temp_env_setup["env_file"]

    # Use monkeypatch to simulate an OSError during Path.mkdir
    def mock_mkdir(*args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    with pytest.raises(ConfigError, match="Failed to create directories"):
        ConfigLoader(dotenv_path=env_file)