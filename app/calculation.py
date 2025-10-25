"""
Defines the data structure for a single calculation.
"""
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from app.operations import Command

@dataclass
class Calculation:
    """
    A data class (struct) to hold the details of a single calculation.
    """
    operand_a: float
    operand_b: float
    command: Command
    result: float
    timestamp: datetime = dataclasses.field(default_factory=datetime.now)

    @property
    def command_name(self) -> str:
        """Returns the name of the command used."""
        return self.command.name

    def __str__(self) -> str:
        """String representation for easy printing."""
        time_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return (
            f"[{time_str}] {self.operand_a} {self.command_name} {self.operand_b} = {self.result}"
        )

    def to_dict(self) -> dict:
        """Converts the record to a dictionary for CSV serialization."""
        return {
            "Timestamp": self.timestamp.isoformat(),
            "OperandA": self.operand_a,
            "OperandB": self.operand_b,
            "Command": self.command_name,
            "Result": self.result
        }