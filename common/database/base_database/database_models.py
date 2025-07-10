"""Models relating to the database"""

from datetime import datetime

from common.enums.database_column_types import DatabaseColumnType
from common.enums.database_tables import Table
from common.helper_functions.date_and_time import (get_string_datetime_now,
                                                   validate_datetime)
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TableColumn(BaseModel):
    """Model for defining a column in a table"""

    name: str = Field(...)
    """The name of the column"""
    type: DatabaseColumnType = Field(...)
    """The datatype for the column"""
    can_be_null: bool = Field(True)
    """Whether or not this column can be null"""
    is_primary_key: bool = Field(False)
    """Whether or not this field is a primary key"""
    is_unique: bool = Field(False)
    """Whether this field must be a unique value"""
    foreign_key_table: Table | None = Field(None)
    """The name of the table that this foreign key goes to"""
    foreign_key_column: str | None = Field(None)
    """The name of the column that this foreign key goes to"""


class DataModel(BaseModel):
    """Model for data in the database"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    id: int = Field(..., ge=-1)  # No ID should be -1, it just allows us to have a default value
    """The ID of the item in the database"""
    created: str = Field(default_factory=get_string_datetime_now)
    """The datetime this item was created"""

    @field_validator("created")
    @classmethod
    def validate_datetime(cls, value: str):
        """Validates a datetime value"""

        return validate_datetime(value)


class UpdateDataModel(BaseModel):
    """Model for updates to data in the database"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
    )
