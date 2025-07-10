"""Database connector for the User Database

This handles operations with the database. This should not be used directly, rather the controllers should be used as a
middle-man.
"""

from os import getenv

from common.auth.password_utils import hash_password
from common.database.base_database.database_adapter import DatabaseAdapter
from common.database.base_database.database_errors import RecordStillExistsError
from common.database.base_database.database_models import TableColumn
from common.database.user_database.user_models import UserModel, UserUpdateModel
from common.enums.database_column_types import DatabaseColumnType
from common.enums.database_tables import Table
from pydantic import BaseModel


class UserDatabaseAdaptor(DatabaseAdapter):
    """Adaptor for the User Database"""

    _table_columns = [
        TableColumn(name="id", type=DatabaseColumnType.INTEGER, is_primary_key=True),
        TableColumn(name="created", type=DatabaseColumnType.TEXT, can_be_null=False),
        TableColumn(name="forename", type=DatabaseColumnType.TEXT, can_be_null=False),
        TableColumn(name="surname", type=DatabaseColumnType.TEXT, can_be_null=False),
        TableColumn(name="email", type=DatabaseColumnType.TEXT, can_be_null=False, is_unique=True),
        TableColumn(name="last_training_date", type=DatabaseColumnType.TEXT, can_be_null=False),
        TableColumn(name="next_training_date", type=DatabaseColumnType.TEXT, can_be_null=False),
        TableColumn(name="permissions", type=DatabaseColumnType.INTEGER, can_be_null=False),
        TableColumn(name="password", type=DatabaseColumnType.TEXT, can_be_null=False),
    ]

    def __init__(self):
        """Initialises the class"""

        super().__init__(Table.USER)

    async def get_all_records(self) -> list[UserModel]:
        """Gets all the records from the database

        :return: The records
        """

        return await self.convert_many_to_model(await self._get_all_records())

    async def get_record_by_id(self, record_id: int) -> UserModel:
        """Gets a record from the database

        :param record_id: The ID of the record to get
        :return: The record
        """

        return await self.convert_data_to_model(await self._get_record_by_id(record_id))

    async def get_record_by_ids(self, **record_ids: dict[str, int]) -> tuple: ...

    async def get_record_by_email(self, email: str) -> UserModel:
        """Gets a record by their email

        :param email: The email of the record to get
        :return: The record
        """

        return await self.convert_data_to_model(await self._get_record_by_field("email", email))

    async def add_record(self, record: UserModel) -> UserModel:
        """Adds a record to the database

        :param record: The record to add
        :return: The data in the database
        """

        record.id = await self.get_next_id()

        return await self.convert_data_to_model(await self._add_record(record.model_dump()))

    async def add_ck_record(self, record: BaseModel, keys: dict[str, int]) -> BaseModel: ...

    async def update_record(self, record_id: int, record_updates: UserUpdateModel) -> UserModel:
        """Updates a record in the database

        :param record_id: The ID of the user to update
        :param record_updates: The updates to the user
        :return: The updated user
        """

        # Check that the user exists
        user_data = (await self.get_record_by_id(record_id)).model_dump()

        update_data = record_updates.model_dump()
        for key, value in update_data.items():
            if value is None:
                update_data[key] = user_data[key]

        return await self.convert_data_to_model(await self._update_record(record_id, update_data))

    async def update_ck_record(self, record_updates: BaseModel, keys: dict[str, int]) -> BaseModel: ...

    async def delete_record(self, record_id: int):
        """Deletes a user from the database

        :param record_id: The user ID to delete
        :return:
        """

        if record_id == 0:
            raise RecordStillExistsError("Cannot delete the admin user")

        await self._delete_record(record_id)

    async def delete_ck_record(self, keys: dict[str, int]): ...

    async def convert_data_to_model(self, data: tuple) -> UserModel:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

        return await self._convert_data_to_model(data, UserModel)

    async def convert_many_to_model(self, data: list[tuple]) -> list[UserModel]:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

        return await super()._convert_many_to_model(data, UserModel)

    async def _add_default_records(self):
        await self.add_record(
            UserModel(
                id=0,
                forename="Admin",
                surname="Admin",
                email=getenv("ADMIN_EMAIL"),
                permissions=0,
                password=await hash_password(getenv("ADMIN_PASSWORD")),
            )
        )
