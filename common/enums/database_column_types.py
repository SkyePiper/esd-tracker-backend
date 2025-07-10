"""Enum for the different column types in the database"""

from enum import StrEnum, auto


class DatabaseColumnType(StrEnum):
    """Enum for the different column types"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    INTEGER = auto()
    """This column is a integer"""
    TEXT = auto()
    """This column is text"""
    BLOB = auto()
    """This column is exactly the same as the inputted data"""
    REAL = auto()
    """This column is a real number"""
    NUMERIC = auto()
    """This column is a number, bool, or date(time)"""
