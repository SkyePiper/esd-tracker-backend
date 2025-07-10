"""Database connector for the User Training Session Interim database

This handles operations with the database. This should not be used directly, rather the controllers should be used as a
middle-man.
"""

from os import getenv
from typing import Any

from common.auth.password_utils import hash_password
from common.database.base_database.database_adapter import DatabaseAdapter
from common.database.base_database.database_models import TableColumn
from common.database.user_database.user_models import UserModel, UserUpdateModel
from common.database.user_session_inter_database.user_session_inter_models import (
    UserSessionInterModel,
    UserSessionInterUpdateModel,
)
from common.enums.database_column_types import DatabaseColumnType
from common.enums.database_tables import Table
from pydantic import BaseModel


class UserSessionInterDatabaseAdapter(DatabaseAdapter):
    """Adaptor for the User Database"""

    _table_columns = [
        TableColumn(name="user_id", type=DatabaseColumnType.INTEGER, foreign_key_table=Table.USER, can_be_null=False),
        TableColumn(
            name="training_session_id",
            type=DatabaseColumnType.INTEGER,
            foreign_key_table=Table.TRAINING_SESSION,
            can_be_null=False,
        ),
        TableColumn(name="user_attendance_type", type=DatabaseColumnType.INTEGER, can_be_null=False),
    ]

    def __init__(self):
        """Initialises the class"""

        super().__init__(Table.USER_SESSION_INTER)

    async def get_all_records(self) -> list[BaseModel]: ...

    async def get_record_by_id(self, record_id: int) -> tuple: ...

    async def get_record_by_ids(self, record_ids: dict[str, int]) -> UserSessionInterModel:
        """Gets a record by the CK IDs

        :param record_ids: The IDs of the CKs to get
        :return: The record
        """

        return await self.convert_data_to_model(await self._get_record_by_ids(record_ids))

    async def get_all_records_with_user_id(self, record_id: int) -> list[UserSessionInterModel]:
        """Gets all the records with a user id

        :param record_id: The user ID to get all the records of
        :return: The records
        """

        return await self.convert_many_to_model(await self._get_many_by_field("user_id", record_id))

    async def get_all_records_with_session_id(self, record_id: int) -> list[UserSessionInterModel]:
        """Gets all the records with a session id

        :param record_id: The session ID to get all the records of
        :return: The records
        """

        return await self.convert_many_to_model(await self._get_many_by_field("training_session_id", record_id))

    async def add_record(self, record: BaseModel) -> BaseModel: ...

    async def add_ck_record(self, record: UserSessionInterModel, keys: dict[str, int]) -> UserSessionInterModel:
        """Adds a record to the database

        :param record: The record to add
        :param keys: The keys that comprise the CK
        :return: The data in the database
        """

        return await self.convert_data_to_model(await self._add_ck_record(record.model_dump(), keys))

    async def update_record(self, record_id: int, record_updates: BaseModel) -> BaseModel: ...

    async def update_ck_record(
        self, record_updates: UserSessionInterUpdateModel, keys: dict[str, int]
    ) -> UserSessionInterModel:
        """Updates a record in the database

        :param record_updates: The updates to the record
        :param keys: The IDs to use to identify the record
        :return: The updated record
        """

        existing_data = (await self.get_record_by_ids(keys)).model_dump()

        update_data = record_updates.model_dump()
        for key, value in update_data.items():
            if value is None:
                update_data[key] = existing_data[key]

        return await self.convert_data_to_model(await self._update_ck_record(keys, update_data))

    async def delete_record(self, record_id: int): ...

    async def delete_ck_record(self, keys: dict[str, int]): ...

    async def convert_data_to_model(self, data: tuple) -> UserSessionInterModel:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

        return await self._convert_data_to_model(data, UserSessionInterModel)

    async def convert_many_to_model(self, data: list[tuple]) -> list[UserSessionInterModel]:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

        return await self._convert_many_to_model(data, UserSessionInterModel)

    async def _add_default_records(self): ...
