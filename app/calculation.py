########################
# Calculation Model
########################

from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict

from app.exceptions import OperationError


@dataclass
class Calculation:
    """
    Value Object representing a single calculation.

    Encapsulates details of a mathematical calculation, including operation,
    operands, result, and timestamp. Supports optional and basic operations.
    """

    operation: str
    operand1: Decimal
    operand2: Decimal
    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        if not hasattr(self, 'result') or self.result is None:
            self.result = self.calculate()

    def __repr__(self):
        return f"{self.timestamp} | {self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def calculate(self) -> Decimal:
        """
        Execute calculation using the specified operation.

        Returns:
            Decimal: Calculation result.

        Raises:
            OperationError: If operation is unknown or invalid.
        """
        operations = {
            "Addition": lambda x, y: x + y,
            "Subtraction": lambda x, y: x - y,
            "Multiplication": lambda x, y: x * y,
            "Division": lambda x, y: x / y if y != 0 else self._raise_div_zero(),
            "Power": lambda x, y: Decimal(pow(float(x), float(y))) if y >= 0 else self._raise_neg_power(),
            "Root": lambda x, y: Decimal(pow(float(x), 1 / float(y))) if x >= 0 and y != 0 else self._raise_invalid_root(x, y),
            "Modulus": lambda x, y: x % y if y != 0 else self._raise_div_zero(),
            "IntegerDivision": lambda x, y: x // y if y != 0 else self._raise_div_zero(),
            "Percentage": lambda x, y: (x / y) * 100 if y != 0 else self._raise_div_zero(),
            "AbsoluteDifference": lambda x, y: abs(x - y)
        }

        op = operations.get(self.operation)
        if not op:
            raise OperationError(f"Unknown operation: {self.operation}")

        try:
            return op(self.operand1, self.operand2)
        except (InvalidOperation, ValueError, ArithmeticError) as e:
            raise OperationError(f"Calculation failed: {str(e)}")

    @staticmethod
    def _raise_div_zero():
        raise OperationError("Division by zero is not allowed")

    @staticmethod
    def _raise_neg_power():
        raise OperationError("Negative exponents are not supported")

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal):
        if y == 0:
            raise OperationError("Zero root is undefined")
        if x < 0:
            raise OperationError("Cannot calculate root of negative number")
        raise OperationError("Invalid root operation")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation,
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        try:
            calc = Calculation(
                operation=data['operation'],
                operand1=Decimal(data['operand1']),
                operand2=Decimal(data['operand2']),
                result=Decimal(data['result'])
            )
            calc.timestamp = datetime.datetime.fromisoformat(data['timestamp'])
            return calc
        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {str(e)}")

    def __str__(self) -> str:
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        try:
            return str(self.result.quantize(Decimal('0.' + '0' * precision)).normalize())
        except InvalidOperation:
            return str(self.result)
