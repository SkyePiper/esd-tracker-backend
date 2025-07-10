"""Enum for the different permissions"""

from enum import IntEnum, auto


class Permissions(IntEnum):
    """Enum for the different permissions a user could have"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return 1 << count

    ADMINISTER = auto()
    """This user can do anything within the application"""
    GET_USER = auto()
    """This user can get users"""
    CREATE_USER = auto()
    """This user can create new users"""
    UPDATE_SELF = auto()
    """This user can update most details about themselves"""
    UPDATE_OTHER_USERS = auto()
    """This user can update other users"""
    DELETE_USERS = auto()
    """This user can delete users"""

    GET_TRAINING_SESSION = auto()
    """This user can get training sessions"""
    CREATE_TRAINING_SESSION = auto()
    """This user can create training sessions"""
    UPDATE_TRAINING_SESSIONS = auto()
    """This user can update training sessions"""
    DELETE_TRAINING_SESSIONS = auto()
    """This user can delete training sessions"""
