########################
# Input Validation     #
########################

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError


@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """
        Validate and convert input to Decimal.

        Args:
            value (Any): Input value to validate
            config (CalculatorConfig): Calculator configuration

        Returns:
            Decimal: Validated and converted number

        Raises:
            ValidationError: If input is invalid or exceeds max allowed value
        """
        try:
            # Strip strings and convert to Decimal
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))

            # Check against maximum allowed input
            if abs(number) > config.max_input_value:
                raise ValidationError(
                    f"Value exceeds maximum allowed: {config.max_input_value}"
                )

            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e
