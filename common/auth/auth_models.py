"""Models used for auth"""

from common.helper_functions.date_and_time import create_user_jwt_expiry_date
from pydantic import BaseModel, EmailStr, Field


class UserJwtDataModel(BaseModel):
    """Model for holding the data for a user in a JWT"""

    user_id: int = Field(...)
    """The ID of the user"""
    user_forename: str = Field(...)
    """The forename of the user"""
    user_surname: str = Field(...)
    """The surname of the user"""
    user_email: EmailStr = Field(...)
    """The email of the user"""
    permissions: int = Field(...)
    """The permissions of the user"""
    expires: str = Field(default_factory=create_user_jwt_expiry_date)
    """The expiry datetime of this token"""


class JwtModel(BaseModel):
    """Model for a JWT"""

    access_token: str = Field(...)
    """The token string"""
    token_type: str = Field("bearer", frozen=True)
    """The type of token this is"""

    data: dict = Field(...)
    """The data of the jwt"""
