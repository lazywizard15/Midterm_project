"""
Calculation record manager for the calculator.
Handles storing, saving, and restoring previous calculations.
"""

import pandas as pd
from datetime import datetime
from typing import List, Optional
from app.calculation import Calculation
from app.operations import OperationFactory
from app.exceptions import CalcHistoryError


class CalcHistory:
    """Manages past calculation records."""
    
    def __init__(self, capacity: int = 100):
        """
        Initialize history manager.
        
        Args:
            capacity: Maximum number of records to keep
        """
        self._records: List[Calculation] = []
        self._capacity = capacity
    
    def record(self, calc: Calculation) -> None:
        """
        Add a new calculation to history.
        
        Args:
            calc: Calculation object to store
        """
        self._records.append(calc)
        if len(self._records) > self._capacity:
            self._records.pop(0)
    
    def get_records(self) -> List[Calculation]:
        """Return a copy of all stored calculations."""
        return self._records.copy()
    
    def last(self) -> Optional[Calculation]:
        """Return the most recent calculation, or None if empty."""
        if not self._records:
            return None
        return self._records[-1]
    
    def count(self) -> int:
        """Return number of stored calculations."""
        return len(self._records)
    
    def erase(self) -> None:
        """Clear all stored calculation records."""
        self._records.clear()
    
    # --- CSV Persistence Methods ---
    def save_csv(self, path: str) -> None:
        """
        Save all records to a CSV file.
        
        Args:
            path: Destination file path
            
        Raises:
            CalcHistoryError: If saving fails or history is empty
        """
        if not self._records:
            raise CalcHistoryError("No records to save")
        
        try:
            data = [c.to_dict() for c in self._records]
            df = pd.DataFrame(data)
            df.to_csv(path, index=False)
        except Exception as e:
            raise CalcHistoryError(f"Failed to save records: {str(e)}")
    
    def load_csv(self, path: str) -> None:
        """
        Load calculation records from a CSV file.
        
        Args:
            path: CSV file path
            
        Raises:
            CalcHistoryError: If loading fails
        """
        try:
            df = pd.read_csv(path)
            self._records.clear()
            
            for _, row in df.iterrows():
                try:
                    op = OperationFactory.create_operation(row['operation'])
                    calc = Calculation(op, float(row['operand_a']), float(row['operand_b']))
                    calc.result = float(row['result'])
                    calc.timestamp = pd.to_datetime(row['timestamp'])
                    self._records.append(calc)
                except Exception:
                    continue  # Skip malformed rows
            
            # Trim to capacity
            if len(self._records) > self._capacity:
                self._records = self._records[-self._capacity:]
        except FileNotFoundError:
            raise CalcHistoryError(f"File not found: {path}")
        except Exception as e:
            raise CalcHistoryError(f"Failed to load records: {str(e)}")
    
    # --- String Representations ---
    def __str__(self) -> str:
        if not self._records:
            return "No calculation records available"
        lines = ["Calculation Records:"]
        for i, rec in enumerate(self._records, 1):
            lines.append(f"{i}. {rec}")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"CalcHistory(size={len(self._records)}, capacity={self._capacity})"
