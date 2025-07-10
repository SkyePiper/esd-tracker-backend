"""Models for the user and training sessions interim table"""

from common.database.base_database.database_models import (DataModel,
                                                           UpdateDataModel)
from common.enums.user_session_attendance import Attendance
from common.responses import SuccessResponseModel
from pydantic import BaseModel, Field


class UserSessionInterModel(BaseModel):
    """Model for the interim between a user and a training session"""

    user_id: int = Field(...)
    """The ID of the user"""
    training_session_id: int = Field(...)
    """The ID of the training session ID"""
    user_attendance_type: Attendance = Field(...)
    """The attendance type of the user"""


class UserSessionInterUpdateModel(UpdateDataModel):
    """Model for updates to the interim between a user and a training session"""

    user_attendance_type: Attendance | None = Field(None)
    """The attendance type of the user"""


class UserSessionInterResponseModel(SuccessResponseModel):
    """Response model for sending data to the frontend"""

    data: UserSessionInterModel = Field(...)
