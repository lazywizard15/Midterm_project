"""
Defines arithmetic operations using the Factory Pattern.
"""
import math
from abc import ABC, abstractmethod
from app.exceptions import OperationError

class Command(ABC):
    """Abstract base class for all commands."""
    
    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Executes the command with two operands."""
        pass # pragma: no cover
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the command (e.g., 'add')."""
        pass # pragma: no cover
    
    def __eq__(self, other):
        """Commands are equal if they are of the same type."""
        return isinstance(other, self.__class__)
    # --- END OF ADDITION ---
# --- Core Operations ---

class AddCommand(Command):
    """Adds two numbers."""
    @property
    def name(self) -> str: return "add"
    
    def execute(self, a: float, b: float) -> float:
        return a + b

class SubtractCommand(Command):
    """Subtracts the second number from the first."""
    @property
    def name(self) -> str: return "subtract"
    
    def execute(self, a: float, b: float) -> float:
        return a - b

class MultiplyCommand(Command):
    """Multiplies two numbers."""
    @property
    def name(self) -> str: return "multiply"
    
    def execute(self, a: float, b: float) -> float:
        return a * b

class DivideCommand(Command):
    """Divides the first number by the second."""
    @property
    def name(self) -> str: return "divide"
    
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Cannot divide by zero.")
        return a / b

# --- New Mandatory Operations ---

class PowerCommand(Command):
    """Raises the first number to the power of the second."""
    @property
    def name(self) -> str: return "power"
    
    def execute(self, a: float, b: float) -> float:
        try:
            return math.pow(a, b)
        except ValueError as e:
            # Handle cases like math.pow(-1, 0.5)
            raise OperationError(f"Math error during power operation: {e}")

class RootCommand(Command):
    """Calculates the nth root of a number (a = number, b = root)."""
    @property
    def name(self) -> str: return "root"
    
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Cannot calculate the 0th root.")
        if a < 0 and b % 2 == 0:
            raise OperationError("Cannot calculate an even root of a negative number.")
        try:
            # b-th root of a is a^(1/b)
            return math.pow(a, 1/b)
        except ValueError as e:
            raise OperationError(f"Math error during root operation: {e}") # pragma: no cover

class ModulusCommand(Command):
    """Computes the remainder of a division."""
    @property
    def name(self) -> str: return "modulus"
    
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Cannot perform modulus by zero.")
        return a % b

class IntDivideCommand(Command):
    """Performs integer division."""
    @property
    def name(self) -> str: return "int_divide"
    
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Cannot perform integer division by zero.")
        return a // b

class PercentageCommand(Command):
    """Calculates the percentage of one number with respect to another (a / b) * 100."""
    @property
    def name(self) -> str: return "percent"
    
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise OperationError("Cannot calculate percentage with respect to zero.")
        return (a / b) * 100

class AbsDiffCommand(Command):
    """Calculates the absolute difference between two numbers."""
    @property
    def name(self) -> str: return "abs_diff"
    
    def execute(self, a: float, b: float) -> float:
        return abs(a - b)

# --- Factory ---

class CommandFactory:
    """
    Factory for creating command instances.
    This uses the Factory Design Pattern.
    """
    def __init__(self):
        # Register all available command classes
        self._commands = {
            cmd.name: cmd
            for cmd in [
                AddCommand(), SubtractCommand(), MultiplyCommand(), DivideCommand(),
                PowerCommand(), RootCommand(), ModulusCommand(), IntDivideCommand(),
                PercentageCommand(), AbsDiffCommand()
            ]
        }

    def get_command(self, command_name: str) -> Command:
        """
        Retrieves a command instance by its name.
        """
        command = self._commands.get(command_name)
        if not command:
            raise OperationError(f"Unknown command: '{command_name}'")
        return command

    def get_available_commands(self) -> list[str]:
        """Returns a list of all registered command names."""
        return list(self._commands.keys())