"""
Arithmetic operations and factory for calculator.
Provides addition, subtraction, multiplication, division, power, root, modulus, integer division, percentage, and absolute difference.
"""

from abc import ABC, abstractmethod
from app.exceptions import OperationError

# Base Operation
class CalcOperation(ABC):
    """Abstract base for all arithmetic operations."""

    @abstractmethod
    def execute(self, x: float, y: float) -> float:
        """Perform the operation on x and y."""
        pass

    @abstractmethod
    def symbol(self) -> str:
        """Return the symbolic representation of the operation."""
        pass

# Concrete Operations
class SumOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        return x + y

    def symbol(self) -> str:
        return "+"

class SubtractOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        return x - y

    def symbol(self) -> str:
        return "-"

class MultiplyOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        return x * y

    def symbol(self) -> str:
        return "*"

class DivideOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        if y == 0:
            raise OperationError("Division by zero is not allowed")
        return x / y

    def symbol(self) -> str:
        return "/"

class IntDivideOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        if y == 0:
            raise OperationError("Cannot divide by zero")
        return x // y

    def symbol(self) -> str:
        return "//"

class ModulusOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        if y == 0:
            raise OperationError("Modulo by zero is invalid")
        return x % y

    def symbol(self) -> str:
        return "%"

class PowerOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        try:
            return x ** y
        except (OverflowError, ValueError) as e:
            raise OperationError(f"Power operation failed: {e}")

    def symbol(self) -> str:
        return "^"

class RootOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        if y == 0:
            raise OperationError("Cannot calculate 0th root")
        if x < 0 and y % 2 == 0:
            raise OperationError("Even root of negative number is invalid")
        return x ** (1 / y)

    def symbol(self) -> str:
        return "√"

class PercentOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        if y == 0:
            raise OperationError("Cannot calculate percentage with denominator zero")
        return (x / y) * 100

    def symbol(self) -> str:
        return "%of"

class AbsDiffOp(CalcOperation):
    def execute(self, x: float, y: float) -> float:
        return abs(x - y)

    def symbol(self) -> str:
        return "|diff|"

# Factory for creating operations
class CalcOpFactory:
    """Factory for generating operation instances based on a name."""

    _operation_map = {
        "add": SumOp,
        "subtract": SubtractOp,
        "multiply": MultiplyOp,
        "divide": DivideOp,
        "power": PowerOp,
        "root": RootOp,
        "modulus": ModulusOp,
        "int_divide": IntDivideOp,
        "percent": PercentOp,
        "abs_diff": AbsDiffOp,
    }

    @classmethod
    def create(cls, op_name: str) -> CalcOperation:
        """Return an operation instance corresponding to the name."""
        op_class = cls._operation_map.get(op_name.lower())
        if op_class is None:
            raise OperationError(f"Unknown operation requested: {op_name}")
        return op_class()

    @classmethod
    def list_operations(cls) -> list:
        """Return all supported operation names."""
        return list(cls._operation_map.keys())
