"""
Tests for app/operations.py
"""
import pytest
from app.operations import CommandFactory
from app.exceptions import OperationError

@pytest.fixture
def factory():
    """Provides a CommandFactory instance for tests."""
    return CommandFactory()

def test_factory_get_known_commands(factory):
    """Tests that the factory can create all known commands."""
    commands = [
        'add', 'subtract', 'multiply', 'divide', 'power', 'root',
        'modulus', 'int_divide', 'percent', 'abs_diff'
    ]
    for cmd_name in commands:
        command = factory.get_command(cmd_name)
        assert command is not None
        assert command.name == cmd_name

def test_factory_get_unknown_command(factory):
    """Tests that the factory raises an error for an unknown command."""
    with pytest.raises(OperationError, match="Unknown command: 'logarithm'"):
        factory.get_command('logarithm')

def test_factory_get_available_commands(factory):
    """Tests retrieving the list of all command names."""
    expected_commands = {
        'add', 'subtract', 'multiply', 'divide', 'power', 'root',
        'modulus', 'int_divide', 'percent', 'abs_diff'
    }
    available_commands = set(factory.get_available_commands())
    assert available_commands == expected_commands

# --- Test Each Operation ---
# Use pytest.mark.parametrize for efficient testing

@pytest.mark.parametrize("cmd_name, a, b, expected", [
    ('add', 5, 3, 8),
    ('add', 5, -3, 2),
    ('subtract', 10, 4, 6),
    ('subtract', 4, 10, -6),
    ('multiply', 6, 7, 42),
    ('multiply', 6, -7, -42),
    ('divide', 10, 2, 5),
    ('divide', 5, 2, 2.5),
    ('power', 2, 3, 8),
    ('power', 4, 0.5, 2),
    ('power', 9, -0.5, 1/3),
    ('root', 8, 3, 2),
    ('root', 16, 2, 4),
    ('root', 16, 4, 2),
    ('modulus', 10, 3, 1),
    ('modulus', 7, 2, 1),
    ('modulus', -7, 2, 1), # Python's % behavior
    ('int_divide', 10, 3, 3),
    ('int_divide', 7, 2, 3),
    ('int_divide', -7, 2, -4), # Python's // behavior
    ('percent', 50, 100, 50),
    ('percent', 10, 200, 5),
    ('percent', 1, 3, (1/3)*100),
    ('abs_diff', 10, 5, 5),
    ('abs_diff', 5, 10, 5),
    ('abs_diff', -5, 10, 15),
    ('abs_diff', -5, -10, 5),
])
def test_all_operations_success(factory, cmd_name, a, b, expected):
    """Tests various successful calculations."""
    command = factory.get_command(cmd_name)
    assert command.execute(a, b) == pytest.approx(expected)

@pytest.mark.parametrize("cmd_name, a, b, error_msg", [
    ('divide', 10, 0, "Cannot divide by zero"),
    ('int_divide', 10, 0, "Cannot perform integer division by zero"),
    ('modulus', 10, 0, "Cannot perform modulus by zero"),
    ('percent', 10, 0, "Cannot calculate percentage with respect to zero"),
    ('root', 10, 0, "Cannot calculate the 0th root"),
    ('root', -4, 2, "Cannot calculate an even root of a negative number"),
    ('power', -1, 0.5, "Math error"), # math.pow(-1, 0.5) is a ValueError
])
def test_all_operations_errors(factory, cmd_name, a, b, error_msg):
    """Tests calculations that should raise OperationError."""
    command = factory.get_command(cmd_name)
    with pytest.raises(OperationError) as e:
        command.execute(a, b)
    assert error_msg in str(e.value)