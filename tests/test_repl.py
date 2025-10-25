"""
Tests for app/repl.py
"""
import sys
import pytest
from unittest.mock import MagicMock, Mock
from io import StringIO
from app.repl import REPL
from app.calculator import Calculator
from app.calculator_config import ConfigLoader
from app.exceptions import HistoryError

@pytest.fixture
def mock_calculator():
    """Mocks the Calculator."""
    return MagicMock(spec=Calculator)

@pytest.fixture
def mock_config():
    """Mocks the ConfigLoader."""
    mock = MagicMock(spec=ConfigLoader)
    mock.get_setting.side_effect = lambda key, default: {
        'CALCULATOR_MAX_INPUT_VALUE': 1e9,
        'CALCULATOR_PRECISION': 4
    }.get(key, default)
    return mock

@pytest.fixture
def repl(mock_calculator, mock_config):
    """Provides a REPL instance with mocked dependencies."""
    return REPL(mock_calculator, mock_config)

def run_repl_commands(repl, commands):
    """Helper function to simulate user input and capture output."""
    
    # Combine commands into a single string with newlines, just like user input
    input_text = "\n".join(commands)
    
    # Use monkeypatch to replace sys.stdin and sys.stdout
    with pytest.MonkeyPatch.context() as m:
        m.setattr('sys.stdin', StringIO(input_text))
        m.setattr('sys.stdout', StringIO())
        
        try:
            repl.run()
        except SystemExit:
            pass # We expect 'exit' to try to stop the test
            
        output = sys.stdout.getvalue()
    
    return output

def test_repl_arithmetic_commands(repl, mock_calculator):
    """Tests all arithmetic commands."""
    mock_calculator.execute_command.return_value = 15.0
    commands = ["add 10 5", "exit"]
    output = run_repl_commands(repl, commands)
    
    mock_calculator.execute_command.assert_called_with('add', 10.0, 5.0)
    assert "Result: 15" in output

    # Test with a float result
    repl.is_running = True
    mock_calculator.execute_command.return_value = 2.5
    commands = ["divide 5 2", "exit"]
    output = run_repl_commands(repl, commands)
    assert "Result: 2.5000" in output

def test_repl_history_commands(repl, mock_calculator):
    """Tests history, clear, undo, redo."""
    
    # Mock return value for history
    mock_calculation = MagicMock()
    mock_calculation.__str__.return_value = "[Test] 1 + 1 = 2"
    mock_calculator.get_history.return_value = [mock_calculation]
    
    commands = ["history", "clear", "undo", "redo", "exit"]
    output = run_repl_commands(repl, commands)
    
    # Check that the mock calculation was printed
    assert "[Test] 1 + 1 = 2" in output
    # Check that calculator methods were called
    mock_calculator.clear_history.assert_called_once()
    mock_calculator.undo.assert_called_once()
    mock_calculator.redo.assert_called_once()
    
    # Test empty history
    repl.is_running = True
    mock_calculator.get_history.return_value = []
    commands = ["history", "exit"]
    output = run_repl_commands(repl, commands)
    assert "History is empty" in output

def test_repl_persistence_commands(repl, mock_calculator, mock_config):
    """Tests save and load."""
    mock_config.get_history_file_path.return_value = "fake/path/history.csv"
    
    commands = ["save", "load", "exit"]
    output = run_repl_commands(repl, commands)
    
    mock_calculator.save_history.assert_called_once()
    mock_calculator.load_history.assert_called_once()
    assert "History saved to fake/path/history.csv" in output
    assert "History loaded" in output

def test_repl_help_command(repl, mock_calculator):
    """Tests the help command."""
    commands = ["help", "exit"]
    output = run_repl_commands(repl, commands)
    assert "--- Available Commands ---" in output
    assert "add <a> <b>" in output
    assert "Exits the application" in output

def test_repl_error_handling(repl, mock_calculator):
    """Tests that REPL catches and prints errors from calculator."""
    mock_calculator.undo.side_effect = HistoryError("Nothing to undo")
    commands = ["undo", "exit"]
    output = run_repl_commands(repl, commands)
    assert "Error: Nothing to undo" in output

def test_repl_invalid_input(repl, mock_calculator):
    """Tests that REPL catches input validation errors."""
    commands = [
        "add 1",       # Not enough args
        "add one two", # Not numbers
        "fakecmd",     # Unknown command
        "",            # Empty input (should be ignored)
        "exit"
    ]
    output = run_repl_commands(repl, commands)
    
    assert "requires exactly 2 numeric arguments" in output
    assert "is not a valid number" in output
    assert "Unknown command: 'fakecmd'" in output
    # Ensure no calculator commands were called
    mock_calculator.execute_command.assert_not_called()