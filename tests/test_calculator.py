"""
Tests for app/calculator.py (including Observer pattern)
"""
import pytest
from unittest.mock import MagicMock, Mock
from app.calculator import Calculator
from app.operations import CommandFactory, AddCommand
from app.history import History
from app.calculation import Calculation
from app.exceptions import OperationError

@pytest.fixture
def mock_factory():
    """Mocks the CommandFactory."""
    return MagicMock(spec=CommandFactory)

@pytest.fixture
def mock_history():
    """Mocks the History."""
    return MagicMock(spec=History)

@pytest.fixture
def calculator(mock_factory, mock_history):
    """Provides a Calculator instance with mocked dependencies."""
    return Calculator(mock_factory, mock_history)

def test_execute_command_success(calculator, mock_factory, mock_history):
    """Tests a successful command execution."""
    mock_command = MagicMock(spec=AddCommand)
    mock_command.execute.return_value = 8.0
    mock_command.name = 'add'
    
    mock_factory.get_command.return_value = mock_command
    
    result = calculator.execute_command('add', 5, 3)
    
    assert result == 8.0
    mock_factory.get_command.assert_called_with('add')
    mock_command.execute.assert_called_with(5, 3)
    
    # Verify history was updated
    mock_history.add_calculation.assert_called_once()
    # Check the calculation object passed to history
    calc_arg = mock_history.add_calculation.call_args[0][0]
    assert isinstance(calc_arg, Calculation)
    assert calc_arg.operand_a == 5
    assert calc_arg.result == 8.0

def test_execute_command_failure(calculator, mock_factory, mock_history):
    """Tests a command execution that fails (e.g., divide by zero)."""
    error = OperationError("Test Error")
    mock_factory.get_command.side_effect = error
    
    with pytest.raises(OperationError, match="Test Error"):
        calculator.execute_command('divide', 10, 0)
        
    # Ensure history was NOT updated on failure
    mock_history.add_calculation.assert_not_called()

def test_history_commands_pass_through(calculator, mock_history):
    """Tests that history commands are passed to the History manager."""
    calculator.get_history()
    mock_history.get_history.assert_called_once()
    
    calculator.clear_history()
    mock_history.clear_history.assert_called_once()
    
    calculator.undo()
    mock_history.undo.assert_called_once()
    
    calculator.redo()
    mock_history.redo.assert_called_once()
    
    calculator.save_history()
    mock_history.save_history_to_csv.assert_called_once()
    
    calculator.load_history()
    mock_history.load_history_from_csv.assert_called_once_with(calculator._factory)

def test_get_available_commands(calculator, mock_factory):
    """Tests pass-through for get_available_commands."""
    mock_factory.get_available_commands.return_value = ['add', 'subtract']
    commands = calculator.get_available_commands()
    assert commands == ['add', 'subtract']
    mock_factory.get_available_commands.assert_called_once()

# --- Observer Pattern Tests ---

@pytest.fixture
def mock_observer():
    """Mocks an Observer."""
    return MagicMock()

def test_observer_attach_detach(calculator, mock_observer):
    """Tests attaching and detaching observers."""
    calculator.attach(mock_observer)
    assert mock_observer in calculator._observers
    
    # Test that attaching twice doesn't add twice
    calculator.attach(mock_observer)
    assert len(calculator._observers) == 1
    
    calculator.detach(mock_observer)
    assert mock_observer not in calculator._observers

def test_observer_notify_on_calculation(calculator, mock_factory, mock_observer):
    """Tests that observers are notified on successful calculation."""
    mock_command = MagicMock(spec=AddCommand)
    mock_command.execute.return_value = 8.0
    mock_command.name = 'add'
    mock_factory.get_command.return_value = mock_command
    
    calculator.attach(mock_observer)
    calculator.execute_command('add', 5, 3)
    
    # Check that observer's update method was called
    mock_observer.update.assert_called_once()
    call_args = mock_observer.update.call_args[0]
    assert call_args[0] == calculator  # subject
    assert call_args[1] == "calculation_performed" # event
    assert isinstance(call_args[2], Calculation) # data
    assert call_args[2].result == 8.0

def test_observer_notify_on_error(calculator, mock_factory, mock_observer):
    """Tests that observers are notified on calculation error."""
    error = OperationError("Div by zero")
    mock_command = MagicMock(spec=AddCommand)
    mock_command.execute.side_effect = error
    mock_factory.get_command.return_value = mock_command
    
    calculator.attach(mock_observer)
    
    with pytest.raises(OperationError):
        calculator.execute_command('divide', 10, 0)
        
    # Check that observer's update method was called with error
    mock_observer.update.assert_called_once_with(calculator, "error_occurred", error)

def test_observer_notify_on_history_changes(calculator, mock_observer):
    """Tests that observers are notified on other history events."""
    calculator.attach(mock_observer)
    
    calculator.clear_history()
    mock_observer.update.assert_called_with(calculator, "history_cleared", None)
    
    calculator.undo()
    mock_observer.update.assert_called_with(calculator, "undo", None)
    
    calculator.redo()
    mock_observer.update.assert_called_with(calculator, "redo", None)
    
    calculator.save_history()
    mock_observer.update.assert_called_with(calculator, "history_saved", None)
    
    calculator.load_history()
    mock_observer.update.assert_called_with(calculator, "history_loaded", None)