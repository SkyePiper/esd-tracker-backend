"""Enums to represent the attendance of a user to a training sessions"""

from enum import IntEnum, auto


class Attendance(IntEnum):
    """The attendance of a user"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 1 << count

    SIGNED_UP = auto()
    """This user is signed up to attend the training session"""
    NO_LONGER_ATTENDING = auto()
    """This used is no longer attending this training session"""
    ATTENDED = auto()
    """This user has attended this training session"""
    NO_SHOW = auto()
    """This user did not attend this training session"""
