"""Models for the user"""

from datetime import datetime

from common.database.base_database.database_models import DataModel, UpdateDataModel
from common.enums.permissions import Permissions
from common.helper_functions.date_and_time import get_string_datetime_now, validate_datetime
from common.responses import BaseResponseModel, SuccessResponseModel
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


class UserModel(DataModel):
    """Model for the user"""

    forename: str = Field(..., min_length=1)
    """The forename of the user"""
    surname: str = Field(..., min_length=1)
    """The surname of the user"""
    email: EmailStr = Field(...)
    """The email of the user"""
    last_training_date: str = Field(default_factory=get_string_datetime_now)
    """The last datetime the user attended ESD training"""
    next_training_date: str = Field(default_factory=get_string_datetime_now)
    """The datetime the user needs to be retrained by"""
    permissions: int = Field(...)
    """The permissions the user has"""
    password: str = Field(...)
    """The users hashed password"""

    @field_validator("last_training_date", "next_training_date")
    @classmethod
    def validate_datetime(cls, value: str):
        """Validates a datetime value"""

        return validate_datetime(value)


class UserUpdateModel(UpdateDataModel):
    """Model for updates to the user"""

    forename: str | None = Field(None)
    """The new forename of the user"""
    surname: str | None = Field(None)
    """The new surname of the user"""
    email: EmailStr | None = Field(None)
    """The new email of the user"""
    last_training_date: str | None = Field(None)
    """The new datetime of the last training that the user attended"""
    next_training_date: str | None = Field(None)
    """The new datetime that the users next training is due"""
    permissions: int | None = Field(None)
    """The new permissions that the user has"""

    @field_validator("last_training_date", "next_training_date")
    @classmethod
    def validate_datetime(cls, value: str | None):
        """Validates a datetime value"""

        if value is None:
            return None

        return validate_datetime(value)


class MinimisedUserDataModel(DataModel):
    """Model for sending only the data needed by other users to the frontend"""

    forename: str | None = Field(None)
    """The new forename of the user"""
    surname: str | None = Field(None)
    """The new surname of the user"""
    email: EmailStr | None = Field(None)
    """The new email of the user"""
    last_training_date: str | None = Field(None)
    """The new datetime of the last training that the user attended"""
    next_training_date: str | None = Field(None)
    """The new datetime that the users next training is due"""
    permissions: int | None = Field(None)
    """The new permissions that the user has"""


class UserResponseModel(SuccessResponseModel):
    """Response model for sending User data to the frontend"""

    data: UserModel = Field(...)


class UsersResponseModel(SuccessResponseModel):
    """Response model for sending multiple users to the frontend"""

    data: list[MinimisedUserDataModel] = Field(...)
