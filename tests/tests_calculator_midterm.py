# tests/test_calculator_midterm.py

import pytest
from decimal import Decimal
from app.calculator_config import CalculatorConfig
from app.calculator import Calculator
from app.operations import OperationFactory
from app.exceptions import OperationError, ValidationError

# ---------------- Setup ---------------- #

@pytest.fixture
def calc():
    config = CalculatorConfig()
    return Calculator(config=config)

# ---------------- Basic Operations ---------------- #

def test_addition(calc):
    calc.set_operation('add')
    result = calc.perform_operation(5, 3)
    assert result == Decimal(8)

def test_subtraction(calc):
    calc.set_operation('subtract')
    result = calc.perform_operation(10, 4)
    assert result == Decimal(6)

def test_multiplication(calc):
    calc.set_operation('multiply')
    result = calc.perform_operation(6, 7)
    assert result == Decimal(42)

def test_division(calc):
    calc.set_operation('divide')
    result = calc.perform_operation(20, 4)
    assert result == Decimal(5)

def test_division_by_zero(calc):
    calc.set_operation('divide')
    with pytest.raises(OperationError):
        calc.perform_operation(10, 0)

# ---------------- Optional Operations ---------------- #

def test_power(calc):
    calc.set_operation('power')
    result = calc.perform_operation(2, 3)
    assert result == Decimal(8)

def test_root(calc):
    calc.set_operation('root')
    result = calc.perform_operation(27, 3)
    assert result == Decimal(3)

def test_modulus(calc):
    calc.set_operation('modulus')
    result = calc.perform_operation(10, 3)
    assert result == Decimal(1)

def test_integer_division(calc):
    calc.set_operation('int_divide')
    result = calc.perform_operation(10, 3)
    assert result == Decimal(3)

def test_percentage(calc):
    calc.set_operation('percent')
    result = calc.perform_operation(50, 200)
    assert result == Decimal(25)

def test_absolute_difference(calc):
    calc.set_operation('abs_diff')
    result = calc.perform_operation(10, 7)
    assert result == Decimal(3)

# ---------------- Undo / Redo ---------------- #

def test_undo_redo(calc):
    calc.set_operation('add')
    calc.perform_operation(1, 1)
    calc.perform_operation(2, 2)
    assert len(calc.history) == 2

    assert calc.undo() is True
    assert len(calc.history) == 1

    assert calc.redo() is True
    assert len(calc.history) == 2

# ---------------- History Management ---------------- #

def test_clear_history(calc):
    calc.set_operation('add')
    calc.perform_operation(5, 5)
    calc.clear_history()
    assert len(calc.history) == 0

# ---------------- Observers / Auto-save ---------------- #

def test_available_operations(calc):
    ops = calc.get_available_operations()
    expected = [
        'add', 'subtract', 'multiply', 'divide', 'power', 'root',
        'modulus', 'int_divide', 'percent', 'abs_diff'
    ]
    for op in expected:
        assert op in ops

# ---------------- Input Validation ---------------- #

def test_input_validation(calc):
    calc.set_operation('add')
    with pytest.raises(ValidationError):
        calc.perform_operation("not_a_number", 5)
