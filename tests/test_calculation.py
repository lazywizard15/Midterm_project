"""
Tests for app/calculation.py
"""
from datetime import datetime
from app.calculation import Calculation
from app.operations import AddCommand

def test_calculation_dataclass():
    """Tests the Calculation data class and its methods."""
    command = AddCommand()
    timestamp = datetime.now()
    
    calc = Calculation(
        operand_a=5,
        operand_b=3,
        command=command,
        result=8,
        timestamp=timestamp
    )
    
    assert calc.operand_a == 5
    assert calc.operand_b == 3
    assert calc.result == 8
    assert calc.command_name == "add"
    
    # Test __str__ method
    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    assert str(calc) == f"[{time_str}] 5 add 3 = 8"
    
    # Test to_dict method
    expected_dict = {
        "Timestamp": timestamp.isoformat(),
        "OperandA": 5,
        "OperandB": 3,
        "Command": "add",
        "Result": 8
    }
    assert calc.to_dict() == expected_dict