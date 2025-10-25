"""
Provides validation functions for user input.
"""
from typing import Optional
from app.exceptions import InputValidationError

class InputHelper:
    """Contains static methods for validating and parsing user input."""
    
    def __init__(self, max_value: float, min_value: float):
        self.max_value = max_value
        self.min_value = min_value

    def parse_operand(self, input_str: Optional[str]) -> float:
        """
        Tries to convert a string to a float and validates it.
        """
        if input_str is None:
            raise InputValidationError("No input provided. Expected a number.")
            
        try:
            value = float(input_str)
        except ValueError:
            raise InputValidationError(f"Invalid input: '{input_str}' is not a valid number.")
        
        if not self.min_value <= value <= self.max_value:
            raise InputValidationError(
                f"Input value {value} is out of range ({self.min_value} to {self.max_value})."
            )
            
        return value

    def parse_command_input(self, user_input: str) -> tuple[str, list[float]]:
        """
        Parses the full REPL input string into a command and numeric operands.
        """
        parts = user_input.strip().split()
        if not parts:
            raise InputValidationError("No command entered.")
            
        command = parts[0].lower()
        args_str = parts[1:]
        
        # Commands that don't need operands
        if command in ('history', 'clear', 'undo', 'redo', 'save', 'load', 'help', 'exit'):
            if args_str:
                raise InputValidationError(f"Command '{command}' does not take any arguments.")
            return command, []
            
        # Commands that need exactly two operands
        if command in (
            'add', 'subtract', 'multiply', 'divide', 'power', 'root', 
            'modulus', 'int_divide', 'percent', 'abs_diff'
        ):
            if len(args_str) != 2:
                raise InputValidationError(
                    f"Command '{command}' requires exactly 2 numeric arguments."
                )
            operands = [self.parse_operand(arg) for arg in args_str]
            return command, operands

        raise InputValidationError(f"Unknown command: '{command}'")