"""
Tests for history observer classes.
"""
import pytest
import logging
from unittest.mock import Mock, patch
from app.history import LoggingObserver, AutoSaveObserver
from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from decimal import Decimal


def test_logging_observer_logs_calculation(caplog):
    observer = LoggingObserver()
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    
    with caplog.at_level(logging.INFO):
        observer.update(calc)
    
    assert "Calculation performed" in caplog.text
    assert "Addition" in caplog.text


def test_logging_observer_no_calculation(caplog):
    observer = LoggingObserver()
    
    with caplog.at_level(logging.INFO):
        observer.update(None)
    
    assert "Calculation performed" not in caplog.text


def test_autosave_observer_triggers_save():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    calculator_mock.config.history_file = '/tmp/test_history.csv'
    calculator_mock.history = []
    observer = AutoSaveObserver(calculator_mock)
    
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    observer.update(calc)
    
    calculator_mock.save_history.assert_called_once()


@patch('logging.info')
def test_autosave_observer_logs_autosave(logging_info_mock):
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    calculator_mock.config.history_file = '/tmp/test_history.csv'
    calculator_mock.history = []
    observer = AutoSaveObserver(calculator_mock)
    
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    observer.update(calc)
    
    logging_info_mock.assert_any_call("History auto-saved")


def test_autosave_observer_does_not_trigger_save_when_disabled():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = False
    calculator_mock.config.history_file = '/tmp/test_history.csv'
    calculator_mock.history = []
    observer = AutoSaveObserver(calculator_mock)
    
    calc = Calculation("add", Decimal("2"), Decimal("3"))
    observer.update(calc)
    
    calculator_mock.save_history.assert_not_called()


def test_autosave_observer_invalid_calculator():
    invalid_calculator = Mock()
    
    with pytest.raises(TypeError, match="Calculator must have 'config' attribute"):
        AutoSaveObserver(invalid_calculator)


def test_autosave_observer_no_calculation():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    calculator_mock.config.history_file = '/tmp/test_history.csv'
    calculator_mock.history = []
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(None)
    
    calculator_mock.save_history.assert_not_called()