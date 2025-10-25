"""
This module defines the Calculation class for representing mathematical calculations.
"""
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging
from app.operations import OperationFactory
from app.exceptions import ValidationError


class Calculation:
    """
    Represents a single calculation with operation, operands, result, and timestamp.
    """

    def __init__(self, operation: str, operand1: Decimal, operand2: Decimal):
        """
        Initialize a Calculation instance.
        
        Args:
            operation (str): The operation name.
            operand1 (Decimal): The first operand.
            operand2 (Decimal): The second operand.
        """
        self.operation = operation
        self.operand1 = operand1
        self.operand2 = operand2
        self.timestamp = datetime.now()
        
        # Compute result
        operation_obj = OperationFactory.create_operation(operation)
        self.result = operation_obj.execute(operand1, operand2)

    def to_dict(self) -> dict:
        """
        Convert the Calculation instance to a dictionary.
        
        Returns:
            dict: Dictionary representation of the calculation.
        """
        return {
            'operation': self.operation,
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Calculation':
        """
        Create a Calculation instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing calculation data.
            
        Returns:
            Calculation: New Calculation instance.
            
        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        try:
            operation = data['operation']
            operand1 = Decimal(str(data['operand1']))
            operand2 = Decimal(str(data['operand2']))
            saved_result = Decimal(str(data['result']))
            
            # Create calculation and compute result
            calc = cls(operation, operand1, operand2)
            
            # Check if saved result matches computed result
            if calc.result != saved_result:
                logging.warning(
                    f"Loaded calculation result {saved_result} differs from computed result {calc.result}"
                )
            
            # Use saved result
            calc.result = saved_result
            
            # Set timestamp if provided
            if 'timestamp' in data:
                calc.timestamp = datetime.fromisoformat(data['timestamp'])
            
            return calc
            
        except (KeyError, ValueError, InvalidOperation) as e:
            raise ValidationError(f"Invalid calculation data: {str(e)}")

    def format_result(self, precision: int = 10) -> str:
        """
        Format the result with specified precision.
        
        Args:
            precision (int): Number of decimal places.
            
        Returns:
            str: Formatted result string.
        """
        return f"{self.result:.{precision}f}".rstrip('0').rstrip('.')

    def __eq__(self, other) -> bool:
        """
        Check equality with another Calculation instance.
        
        Args:
            other: Another Calculation instance.
            
        Returns:
            bool: True if calculations are equal, False otherwise.
        """
        if not isinstance(other, Calculation):
            return False
        return (self.operation == other.operation and
                self.operand1 == other.operand1 and
                self.operand2 == other.operand2 and
                self.result == other.result)

    def __repr__(self) -> str:
        """
        Return a string representation of the Calculation.
        
        Returns:
            str: String representation.
        """
        return f"Calculation({self.operation}, {self.operand1}, {self.operand2}) = {self.result}"