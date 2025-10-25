"""
Tests for app/history.py (Memento Pattern and Pandas)
"""
import pytest
import pandas as pd
from app.history import History
from app.calculation import Calculation
from app.operations import AddCommand, SubtractCommand, CommandFactory
from app.exceptions import HistoryError

# Mock ConfigLoader
class MockConfig:
    def __init__(self, tmp_path):
        self._history_file_path = tmp_path / "data" / "history.csv"
        # Use a small size for easy testing
        self._settings = {
            'CALCULATOR_MAX_HISTORY_SIZE': 3,
            'CALCULATOR_DEFAULT_ENCODING': 'utf-8'
        }
        
    def get_setting(self, key, default=None):
        return self._settings.get(key, default)
        
    def get_history_file_path(self):
        return self._history_file_path

@pytest.fixture
def config(tmp_path):
    """Provides a mock config using pytest's tmp_path."""
    return MockConfig(tmp_path)

@pytest.fixture
def command_factory():
    """Provides a real CommandFactory."""
    return CommandFactory()
    
@pytest.fixture
def history(config):
    """Provides a History instance."""
    return History(config)

@pytest.fixture
def sample_calculations():
    """Provides sample Calculation instances."""
    return [
        Calculation(1, 2, AddCommand(), 3),
        Calculation(5, 3, SubtractCommand(), 2)
    ]

def test_add_calculation(history, sample_calculations):
    """Tests adding calculations to the history."""
    calc1, calc2 = sample_calculations
    
    history.add_calculation(calc1)
    assert history.get_history() == [calc1]
    assert len(history._undo_stack) == 1
    
    history.add_calculation(calc2)
    assert history.get_history() == [calc1, calc2]
    assert len(history._undo_stack) == 2

def test_history_max_size(history, sample_calculations):
    """Tests that history size is enforced (max_size=3 from mock config)."""
    calc1, calc2 = sample_calculations
    calc3 = Calculation(10, 10, AddCommand(), 20)
    calc4 = Calculation(20, 10, SubtractCommand(), 10)

    history.add_calculation(calc1)
    history.add_calculation(calc2)
    history.add_calculation(calc3)
    assert history.get_history() == [calc1, calc2, calc3]
    
    # Adding a 4th should pop the 1st
    history.add_calculation(calc4)
    assert history.get_history() == [calc2, calc3, calc4]

def test_clear_history(history, sample_calculations):
    """Tests clearing the history."""
    for calc in sample_calculations:
        history.add_calculation(calc)
        
    assert len(history.get_history()) == 2
    
    history.clear_history()
    assert len(history.get_history()) == 0
    # Check that clear added to undo stack
    assert len(history._undo_stack) == 3 # 2 adds + 1 clear

def test_clear_empty_history(history):
    """Tests that clearing an empty history does nothing."""
    assert len(history.get_history()) == 0
    history.clear_history()
    assert len(history.get_history()) == 0
    assert len(history._undo_stack) == 0

# --- Memento (Undo/Redo) Tests ---

def test_undo_redo(history, sample_calculations):
    """Tests the full undo/redo cycle."""
    calc1, calc2 = sample_calculations
    
    history.add_calculation(calc1)
    history.add_calculation(calc2)
    
    assert history.get_history() == [calc1, calc2]
    
    # 1. Undo last add (calc2)
    history.undo()
    assert history.get_history() == [calc1]
    assert len(history._undo_stack) == 1
    assert len(history._redo_stack) == 1
    
    # 2. Undo again (calc1)
    history.undo()
    assert history.get_history() == []
    assert len(history._undo_stack) == 0
    assert len(history._redo_stack) == 2
    
    # 3. Redo (calc1)
    history.redo()
    assert history.get_history() == [calc1]
    assert len(history._undo_stack) == 1
    assert len(history._redo_stack) == 1

    # 4. Redo again (calc2)
    history.redo()
    assert history.get_history() == [calc1, calc2]
    assert len(history._undo_stack) == 2
    assert len(history._redo_stack) == 0

def test_new_action_clears_redo(history, sample_calculations):
    """Tests that a new action after undo clears the redo stack."""
    calc1, calc2 = sample_calculations
    history.add_calculation(calc1)
    history.add_calculation(calc2)
    
    history.undo() # Undo calc2
    assert len(history._redo_stack) == 1 # calc2 state is in redo
    
    # Add a new calculation
    calc3 = Calculation(10, 10, AddCommand(), 20)
    history.add_calculation(calc3)
    
    assert history.get_history() == [calc1, calc3]
    # Redo stack should now be empty
    assert len(history._redo_stack) == 0
    
    # Trying to redo should fail
    with pytest.raises(HistoryError, match="Nothing to redo"):
        history.redo()

def test_undo_redo_errors(history):
    """Tests errors for empty undo/redo stacks."""
    with pytest.raises(HistoryError, match="Nothing to undo"):
        history.undo()
        
    with pytest.raises(HistoryError, match="Nothing to redo"):
        history.redo()

# --- Persistence (CSV) Tests ---

def test_save_and_load_history(history, sample_calculations, command_factory, config):
    """Tests saving history to CSV and loading it back."""
    for calc in sample_calculations:
        history.add_calculation(calc)
        
    history.save_history_to_csv()
    
    history_file = config.get_history_file_path()
    assert history_file.exists()
    
    # Verify content with pandas
    df = pd.read_csv(history_file)
    assert len(df) == 2
    assert df.iloc[0]["Command"] == "add"
    assert df.iloc[1]["Result"] == 2.0
    
    # Create a new log and load from the file
    new_log = History(config)
    new_log.load_history_from_csv(command_factory)
    
    # Verify loaded history
    loaded_history = new_log.get_history()
    assert len(loaded_history) == 2
    assert loaded_history[0].command_name == "add"
    assert loaded_history[1].operand_a == 5
    
    # Check that loading adds to the undo stack
    assert len(new_log._undo_stack) == 1

def test_save_empty_history(history, config, command_factory):
    """Tests saving when history is empty."""
    history_file = config.get_history_file_path()
    assert not history_file.exists()
    
    history.save_history_to_csv()
    # Should create an empty file
    assert history_file.exists()
    df = pd.read_csv(history_file)
    assert df.empty
    
    # Test loading from this empty file
    new_log = History(config)
    new_log.load_history_from_csv(command_factory)
    assert new_log.get_history() == []


def test_load_nonexistent_file(history, command_factory):
    """Tests loading from a file that doesn't exist (should be fine)."""
    # This should not raise an error, just result in an empty history
    history.load_history_from_csv(command_factory)
    assert history.get_history() == []

def test_load_malformed_file(history, command_factory, config):
    """Tests loading from a malformed CSV."""
    history_file = config.get_history_file_path()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, 'w') as f:
        f.write("HeaderA,HeaderB\nValueA,ValueB,ValueC") # Wrong number of columns
        
    with pytest.raises(HistoryError, match="Failed to parse history file"):
        history.load_history_from_csv(command_factory)