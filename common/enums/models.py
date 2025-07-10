"""Models for the enums"""

from common.responses import SuccessResponseModel
from pydantic import BaseModel, Field


class EnumItemModel(BaseModel):
    """Model for an item in an enum"""

    name: str = Field(...)
    """The name of the enum item"""
    value: int | str = Field(...)
    """The value of the enum item"""


class EnumModel(BaseModel):
    """Model for an enum"""

    enum_name: str = Field(...)
    """The name of the enum"""
    enum_items: list[EnumItemModel] = Field(...)
    """The items in this enum"""


class EnumResponseModel(SuccessResponseModel):
    """Model for sending data about an enum"""

    data: EnumModel = Field(...)
