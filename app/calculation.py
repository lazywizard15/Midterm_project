"""
Represents a single arithmetic operation with operands, result, and timestamp.
"""

from datetime import datetime
from app.operations import Operation


class CalcRecord:
    """Holds details for a single calculation event."""

    def __init__(self, op: Operation, first_num: float, second_num: float):
        """
        Initialize a calculation record.

        Args:
            op: Operation instance to perform
            first_num: First numeric operand
            second_num: Second numeric operand
        """
        self.op_instance = op
        self.num1 = first_num
        self.num2 = second_num
        self.output = None
        self.time_created = datetime.now()

    def run(self) -> float:
        """
        Execute the calculation using the operation.

        Returns:
            Computed result
        """
        self.output = self.op_instance.execute(self.num1, self.num2)
        return self.output

    def __str__(self) -> str:
        """Readable string for display purposes."""
        symbol = self.op_instance.get_symbol()
        if self.output is not None:
            return f"{self.num1} {symbol} {self.num2} = {self.output}"
        return f"{self.num1} {symbol} {self.num2}"

    def __repr__(self) -> str:
        """Detailed developer-friendly representation."""
        return (f"CalcRecord({self.op_instance.__class__.__name__}, "
                f"{self.num1}, {self.num2}, output={self.output})")

    def as_dict(self) -> dict:
        """
        Convert calculation to a dictionary for saving or serialization.

        Returns:
            Dictionary with operation name, operands, result, and timestamp
        """
        return {
            'operation': self.op_instance.__class__.__name__.replace('Operation', '').lower(),
            'num1': self.num1,
            'num2': self.num2,
            'output': self.output,
            'time_created': self.time_created.isoformat()
        }
