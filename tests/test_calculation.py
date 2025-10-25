"""
Unit tests for CalcRecord class.
"""

import pytest
from datetime import datetime
from app.calculation import CalcRecord
from app.operations import AddOperation, MultiplyOperation, DivideOperation
from app.exceptions import OperationError


class TestCalcRecord:
    """Tests for CalcRecord class."""

    def test_record_initialization(self):
        """Test that CalcRecord initializes correctly."""
        op = AddOperation()
        record = CalcRecord(op, 5, 3)

        assert record.op_instance == op
        assert record.num1 == 5
        assert record.num2 == 3
        assert record.output is None
        assert isinstance(record.time_created, datetime)

    def test_record_run(self):
        """Test that CalcRecord executes correctly."""
        op = AddOperation()
        record = CalcRecord(op, 5, 3)

        result = record.run()

        assert result == 8
        assert record.output == 8

    def test_record_run_multiply(self):
        """Test CalcRecord with multiplication."""
        op = MultiplyOperation()
        record = CalcRecord(op, 4, 7)

        result = record.run()

        assert result == 28
        assert record.output == 28

    def test_record_run_with_error(self):
        """Test that operation errors propagate."""
        op = DivideOperation()
        record = CalcRecord(op, 10, 0)

        with pytest.raises(OperationError):
            record.run()

    def test_record_str_with_output(self):
        """Test string representation with output."""
        op = AddOperation()
        record = CalcRecord(op, 5, 3)
        record.run()

        result_str = str(record)

        assert "5" in result_str
        assert "3" in result_str
        assert "8" in result_str
        assert "+" in result_str

    def test_record_str_without_output(self):
        """Test string representation without output."""
        op = AddOperation()
        record = CalcRecord(op, 5, 3)

        result_str = str(record)

        assert "5" in result_str
        assert "3" in result_str
        assert "+" in result_str

    def test_record_repr(self):
        """Test detailed representation."""
        op = AddOperation()
        record = CalcRecord(op, 5, 3)
        record.run()

        repr_str = repr(record)

        assert "CalcRecord" in repr_str
        assert "AddOperation" in repr_str
        assert "5" in repr_str
        assert "3" in repr_str

    def test_record_as_dict(self):
        """Test conversion to dictionary."""
        op = AddOperation()
        record = CalcRecord(op, 5, 3)
        record.run()

        record_dict = record.as_dict()

        assert record_dict['operation'] == 'add'
        assert record_dict['num1'] == 5
        assert record_dict['num2'] == 3
        assert record_dict['output'] == 8
        assert 'time_created' in record_dict

    def test_record_as_dict_before_run(self):
        """Test as_dict before execution."""
        op = MultiplyOperation()
        record = CalcRecord(op, 4, 5)

        record_dict = record.as_dict()

        assert record_dict['operation'] == 'multiply'
        assert record_dict['num1'] == 4
        assert record_dict['num2'] == 5
        assert record_dict['output'] is None
        assert 'time_created' in record_dict
