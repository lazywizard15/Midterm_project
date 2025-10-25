"""
Tests for app/input_validators.py
"""
import pytest
from app.input_validators import InputHelper
from app.exceptions import InputValidationError

@pytest.fixture
def validator():
    """Provides an InputHelper instance with a test range of -1000 to 1000."""
    return InputHelper(max_value=1000.0, min_value=-1000.0)

# --- Tests for parse_operand ---

@pytest.mark.parametrize("input_str, expected", [
    ("5", 5.0),
    ("3.14", 3.14),
    ("-10", -10.0),
    ("1000", 1000.0),
    ("-1000", -1000.0),
    ("0", 0.0)
])
def test_parse_operand_success(validator, input_str, expected):
    """Tests successful operand parsing."""
    assert validator.parse_operand(input_str) == expected

@pytest.mark.parametrize("input_str, error_msg", [
    (None, "No input provided"),
    ("abc", "is not a valid number"),
    ("5a", "is not a valid number"),
    ("1001", "out of range"),
    ("-1001", "out of range")
])
def test_parse_operand_failure(validator, input_str, error_msg):
    """Tests failed operand parsing due to invalid format or range."""
    with pytest.raises(InputValidationError) as e:
        validator.parse_operand(input_str)
    assert error_msg in str(e.value)

# --- Tests for parse_command_input ---

@pytest.mark.parametrize("command_name", [
    'add', 'subtract', 'multiply', 'divide', 'power', 'root',
    'modulus', 'int_divide', 'percent', 'abs_diff'
])
def test_parse_command_arithmetic_success(validator, command_name):
    """Tests successful parsing of all 2-operand arithmetic commands."""
    user_input = f"{command_name} 10 5"
    command, operands = validator.parse_command_input(user_input)
    assert command == command_name
    assert operands == [10.0, 5.0]

@pytest.mark.parametrize("command_name", [
    'history', 'clear', 'undo', 'redo', 'save', 'load', 'help', 'exit'
])
def test_parse_command_no_ops_success(validator, command_name):
    """Tests successful parsing of all 0-operand commands."""
    command, operands = validator.parse_command_input(command_name)
    assert command == command_name
    assert operands == []

def test_parse_command_formatting(validator):
    """Tests robustness against extra whitespace and case insensitivity."""
    user_input = "  AdD   5.5   -3  "
    command, operands = validator.parse_command_input(user_input)
    assert command == 'add'
    assert operands == [5.5, -3.0]

@pytest.mark.parametrize("user_input, error_msg", [
    ("", "No command entered"),
    ("   ", "No command entered"),
    ("foo 1 2", "Unknown command: 'foo'"),
    ("add 5", "requires exactly 2"),
    ("add 5 3 1", "requires exactly 2"),
    ("add 5 abc", "is not a valid number"),
    ("add 9999 1", "out of range"),
    ("history 5", "does not take any arguments"),
    ("exit 1 2", "does not take any arguments")
])
def test_parse_command_input_failure(validator, user_input, error_msg):
    """Tests various invalid command input formats."""
    with pytest.raises(InputValidationError) as e:
        validator.parse_command_input(user_input)
    assert error_msg in str(e.value)