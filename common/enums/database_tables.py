"""Enum representing the tables in the database"""

from enum import StrEnum, auto


class Table(StrEnum):
    """Enum representing the name of the tables"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    USER = auto()
    """The user table"""
    TRAINING_SESSION = auto()
    """The Training Session table"""
    USER_SESSION_INTER = auto()
    """The interim table between the user and training sessions"""
