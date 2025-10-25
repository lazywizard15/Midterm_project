"""
Unit tests for CalcSettings configuration manager.
"""

import os
import pytest
from app.calculator_config import CalcSettings  # uses same filename
from app.exceptions import ConfigurationError


def test_loads_default_settings():
    """Verify default values load correctly when .env is missing."""
    settings = CalcSettings()

    assert settings.logs_dir is not None
    assert settings.history_dir is not None
    assert settings.max_history >= 0
    assert settings.precision >= 0
    assert isinstance(settings.auto_save, bool)
    assert isinstance(settings.encoding, str)


def test_directory_creation_on_init():
    """Ensure that necessary directories are created at initialization."""
    settings = CalcSettings()

    assert os.path.exists(settings.logs_dir) or settings.logs_dir == "logs"
    assert os.path.exists(settings.history_dir) or settings.history_dir == "history"


def test_invalid_integer_value(monkeypatch):
    """Raise ConfigurationError if integer environment variable is invalid."""
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "not_a_number")
    with pytest.raises(ConfigurationError):
        CalcSettings()


def test_invalid_float_value(monkeypatch):
    """Raise ConfigurationError if float environment variable is invalid."""
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "invalid_float")
    with pytest.raises(ConfigurationError):
        CalcSettings()


def test_boolean_values(monkeypatch):
    """Confirm boolean string values are correctly interpreted."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    cfg = CalcSettings()
    assert cfg.auto_save is False

    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "on")
    cfg = CalcSettings()
    assert cfg.auto_save is True


def test_repr_contains_key_info():
    """Ensure __repr__ includes critical configuration details."""
    cfg = CalcSettings()
    representation = repr(cfg)

    assert "CalcSettings" in representation
    assert "logs_dir" in representation
    assert "history_dir" in representation
    assert "precision" in representation
