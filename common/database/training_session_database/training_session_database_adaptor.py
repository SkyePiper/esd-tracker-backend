"""Database connector for the User Database"""

from common.database.base_database.database_adapter import DatabaseAdapter
from common.database.base_database.database_models import TableColumn
from common.database.training_session_database.training_session_models import (
    TrainingSessionModel,
    TrainingSessionUpdateModel,
)
from common.enums.database_column_types import DatabaseColumnType
from common.enums.database_tables import Table
from pydantic import BaseModel


class TrainingSessionDatabaseAdaptor(DatabaseAdapter):
    """Adaptor for the Training Session Database"""

    _table_columns = [
        TableColumn(name="id", type=DatabaseColumnType.INTEGER, is_primary_key=True),
        TableColumn(name="created", type=DatabaseColumnType.TEXT, can_be_null=False),
        TableColumn(name="datetime", type=DatabaseColumnType.INTEGER, can_be_null=False),
    ]

    def __init__(self):
        """Initialises the class"""

        super().__init__(Table.TRAINING_SESSION)

    async def get_all_records(self) -> list[TrainingSessionModel]:
        """Gets all the records from the database

        :return: The records
        """

        return await self.convert_many_to_model(await self._get_all_records())

    async def get_record_by_id(self, record_id: int) -> TrainingSessionModel:
        """Gets a record from the database

        :param record_id: The ID of the record to get
        :return: The record
        """

        return await self.convert_data_to_model(await self._get_record_by_id(record_id))

    async def get_record_by_ids(self, record_ids: dict[str, int]) -> tuple: ...

    async def add_record(self, record: TrainingSessionModel) -> TrainingSessionModel:
        """Adds a record to the database

        :param record: The record to add
        :return: The data in the database
        """

        record.id = await self.get_next_id()

        return await self.convert_data_to_model(await self._add_record(record.model_dump()))

    async def add_ck_record(self, record: BaseModel, keys: dict[str, int]) -> BaseModel: ...

    async def update_record(self, record_id: int, record_updates: TrainingSessionUpdateModel) -> TrainingSessionModel:
        """Updates a record in the database

        :param record_id: The ID of the record
        :param record_updates: The updates to the record
        :return: The updated record
        """

        # Check that the session exists
        session_data = (await self.get_record_by_id(record_id)).model_dump()

        update_data = record_updates.model_dump()
        for key, value in update_data.items():
            if value is None:
                update_data[key] = session_data[key]

        return await self.convert_data_to_model(await self._update_record(record_id, update_data))

    async def update_ck_record(self, record_updates: BaseModel, keys: dict[str, int]) -> BaseModel: ...

    async def delete_record(self, record_id: int):
        """Deletes a record from the database

        :param record_id: The ID of the record to delete
        :return:
        """

        await self._delete_record(record_id)

    async def delete_ck_record(self, keys: dict[str, int]): ...

    async def convert_data_to_model(self, data: tuple) -> TrainingSessionModel:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

        return await self._convert_data_to_model(data, TrainingSessionModel)

    async def convert_many_to_model(self, data: list[tuple]) -> list[TrainingSessionModel]:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

        return await self._convert_many_to_model(data, TrainingSessionModel)

    async def _add_default_records(self): ...
