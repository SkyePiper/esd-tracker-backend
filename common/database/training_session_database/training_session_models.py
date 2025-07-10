"""Models for the training sessions"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ...enums.user_session_attendance import Attendance
from ...helper_functions.date_and_time import (get_string_datetime_now,
                                               validate_datetime)
from ...responses import SuccessResponseModel
from ..base_database.database_models import DataModel, UpdateDataModel
from ..user_session_inter_database.user_session_inter_models import \
    UserSessionInterModel


class TrainingSessionModel(DataModel):
    """Model for a training session"""

    datetime: str = Field(default_factory=get_string_datetime_now)

    @field_validator("datetime")
    @classmethod
    def validate_datetime(cls, value: str):
        """Validates a datetime value"""

        return validate_datetime(value)


class TrainingSessionUpdateModel(UpdateDataModel):
    """Model for updating a training session"""

    datetime: str | None = Field(None)

    @field_validator("datetime")
    @classmethod
    def validate_datetime(cls, value: str | None):
        """Validates a datetime value"""

        if value is None:
            return None

        return validate_datetime(value)


class TrainingSessionResponseModel(SuccessResponseModel):
    """Response model for sending Training Session data to the frontend"""

    data: TrainingSessionModel = Field(...)


class TrainingSessionsResponseModel(SuccessResponseModel):
    """Response model for sending multiple training sessions to the frontend"""

    data: list[TrainingSessionModel] = Field(...)


class TrainingSessionUserModel(BaseModel):
    """Model for a user with a attendance record for a training session"""

    training_session_id: int = Field(...)
    """The ID of the training session"""
    forename: str = Field(...)
    """The forename of the user"""
    surname: str = Field(...)
    """The surname of the user"""
    email: EmailStr = Field(...)
    """The email of the user"""
    attendance_type: Attendance = Field(...)
    """The type of attendance marked for this user"""


class TrainingSessionAttendanceResponseModel(SuccessResponseModel):
    """Response model for sending data about the attendance to a training session"""

    data: list[TrainingSessionUserModel] = Field(...)


class TrainingSessionUserAttendanceResponseModel(SuccessResponseModel):
    """Response model for sending data about a users attendance to training sessions"""

    data: list[UserSessionInterModel] = Field(...)
