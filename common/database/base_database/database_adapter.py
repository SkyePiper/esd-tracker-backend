"""Abstract database connector

This handles operations with the database. This should not be used directly, rather the controllers should be used as a
middle-man.
"""

from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from os import getenv
from pathlib import Path
from typing import Any, Coroutine

from aiosqlite import Connection, Cursor, connect
from common.database.base_database.database_errors import RecordDoesNotExistError, RecordStillExistsError
from common.database.base_database.database_models import TableColumn
from common.enums.database_tables import Table
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class DatabaseAdapter(ABC):
    """Abstract database adapter"""

    __database_path: Path = Path("esdTrackerDb.sqlite")
    """The path to the database"""
    _database: Connection = connect(__database_path)
    """The connection to the database, shared between all instances of this class"""
    _cursor: Cursor
    """The cursor for the table"""

    _table: str
    """The table this adaptor is for"""

    _table_columns: list[TableColumn]
    """The columns for the table"""

    __instance: DatabaseAdapter | None = None
    """Whether there is an instance of this adaptor"""

    def __init__(self, table: Table):
        """Initialises the class

        :param table: The table to connect to
        """

        self._table = table

    @property
    def database_path(self) -> Path:
        """Gets the path to the database

        :return: the database path
        :rtype: Path
        """

        return self.__database_path

    @database_path.setter
    def database_path(self, value: Path):
        """Sets the path to the database. This will also update the connection to use the new path

        :param value: The new path
        :type value: Path
        :return:
        :rtype:
        """

        if getenv("UNIT_TESTS") != "TRUE":
            return

        if not isinstance(value, Path):
            raise ValueError(f"Invalid type for database_path: {type(value)} - Expected Path")

        self.__database_path = value
        self._database = connect(value)

    @property
    def table(self) -> str:
        """Gets the table name for this database adapter

        :return: The table name for this database adapter
        :rtype: str
        """

        return self._table

    async def load_db(self):
        """Loads the database

        :return:
        """

        self._database = await connect(self.__database_path)
        self._cursor = await self._database.cursor()

        # Check if the table exists, and if not create it
        table = await (
            await self._cursor.execute(
                f"""
                SELECT
                    tbl_name
                FROM
                    sqlite_master
                WHERE
                    type='table'
                AND
                    tbl_name='{self._table}';
                """
            )
        ).fetchone()

        if table is None:
            await self._cursor.execute(
                f"CREATE TABLE {self._table} \n({await self.__generate_table_columns_string()}\n)"
            )
            await self._database.commit()

            # Reload the database
            await self.load_db()

            await self._add_default_records()

    async def get_count(self) -> int:
        """Gets the count of records in the database

        :return: The number of records
        """

        return (await (await self._cursor.execute(f"SELECT COUNT(*) FROM {self._table}")).fetchone())[0]

    async def get_next_id(self) -> int:
        """Gets the next ID from the database

        :return: The next ID
        """

        next_id = await (
            await self._cursor.execute(
                f"""
            SELECT id
            FROM {self._table}
            ORDER BY id DESC
            LIMIT 1
            """
            )
        ).fetchone()

        if next_id is None:
            # Assume no items in db
            return 0

        return next_id[0] + 1

    @abstractmethod
    async def get_all_records(self) -> list[BaseModel]:
        """Gets all the records from the database

        :return: The records
        """

    @abstractmethod
    async def get_record_by_id(self, record_id: int) -> BaseModel:
        """Gets a record from the database

        :param record_id: The ID of the record to get
        :return: The record
        """

    @abstractmethod
    async def get_record_by_ids(self, record_ids: dict[str, int]) -> BaseModel:
        """Gets a record by the CK IDs

        :param record_ids: The IDs of the CKs to get
        :return: The record
        """

    @abstractmethod
    async def add_record(self, record: BaseModel) -> BaseModel:
        """Adds a record to the database

        :param record: The record to add
        :return: The data in the database
        """

    @abstractmethod
    async def add_ck_record(self, record: BaseModel, keys: dict[str, int]) -> BaseModel:
        """Adds a record to the database

        :param record: The record to add
        :param keys: The keys that comprise the CK
        :return: The data in the database
        """

    @abstractmethod
    async def update_record(self, record_id: int, record_updates: BaseModel) -> BaseModel:
        """Updates a record in the database

        :param record_id: The ID of the record
        :param record_updates: The updates to the record
        :return: The updated record
        """

    @abstractmethod
    async def update_ck_record(self, record_updates: BaseModel, keys: dict[str, int]) -> BaseModel:
        """Updates a record in the database

        :param keys: The keys to use to identify the record
        :param record_updates: The updates to the record
        :return: The updated record
        """

    @abstractmethod
    async def delete_record(self, record_id: int):
        """Deletes a record from the database

        :param record_id: The ID of the record to delete
        :return:
        """

    @abstractmethod
    async def delete_ck_record(self, keys: dict[str, int]):
        """Deletes a record from the database

        :param keys: The keys that comprise the CK
        :return:
        """

    @abstractmethod
    async def convert_data_to_model(self, data: tuple) -> BaseModel:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

    @abstractmethod
    async def convert_many_to_model(self, data: list[tuple]) -> list[BaseModel]:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :return: The model
        """

    @staticmethod
    async def _convert_data_to_model(data: tuple, model: type(BaseModel)) -> Any:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :param model: The model to convert the data to
        :return: The model
        """

        fields = list(model.model_fields.keys())

        model_dict = {}

        for index, item in enumerate(data):
            model_dict[fields[index]] = item

        return model(**model_dict)

    @staticmethod
    async def _convert_many_to_model(data: list[tuple], model: type(BaseModel)) -> list[Any]:
        """Converts data retrieved from a database to a model

        :param data: The data to convert
        :param model: The model to convert the data to
        :return: The model
        """

        fields = list(model.model_fields.keys())
        model_dict = {item: None for item in fields}
        output = []

        for data_item in data:
            new_item = model_dict.copy()

            for index, item in enumerate(data_item):
                new_item[fields[index]] = item

            output.append(model(**new_item))

        return output

    async def _execute_query(self, query: str) -> Cursor:
        """Executes a query

        :param query: The query to execute
        :return: The data received from the database
        """

        return await self._cursor.execute(query)

    async def _get_all_records(self) -> list[tuple]:
        """Gets all the records from the database

        :return: The records
        """

        data = await (
            await self._execute_query(
                f"""
                SELECT *
                FROM {self._table}
                """
            )
        ).fetchall()

        return [tuple(item) for item in data]

    async def _get_record_by_id(self, record_id: int) -> tuple:
        """Gets a record from the database by its ID

        :param record_id: The ID of the record to get
        :return: The record
        :raises RecordDoesNotExistError: If the record does not exist
        """

        data = await (
            await self._execute_query(
                f"""
                SELECT *
                FROM {self._table}
                WHERE
                    id={record_id}
                """
            )
        ).fetchone()

        if data is None:
            raise RecordDoesNotExistError(f"No record with an ID of {record_id} exists")

        return tuple(data)

    async def _get_record_by_ids(self, record_ids: dict[str, int]) -> tuple:
        """Gets a record by its Composite Key IDs

        :param record_ids: The IDs to use
        :return: The record
        :raises RecordDoesNotExistError: If the record does not exist
        """

        data = await (
            await self._execute_query(
                f"""
                SELECT *
                FROM {self._table}
                WHERE (
                    {'\n\t'.join(f"{key}='{value}' AND " for key, value in record_ids.items()).strip('AND ')}
                )
                """
            )
        ).fetchone()

        if data is None:
            raise RecordDoesNotExistError(
                f"No record with the IDs of {'; '.join(f'{key}: {value}' for key, value in record_ids.items())} exists"
            )

        return tuple(data)

    async def _get_record_by_field(self, field: str, value: str) -> tuple:
        """Gets a record by a given field. Will retrieve the first match, even if many exist

        :param field: The field to match the value of
        :param value: The value to match
        :return: The record
        :raises RecordDoesNotExistError: If no record matches the value fo the given field
        """

        data = await (
            await self._execute_query(
                f"""
                SELECT *
                FROM {self._table}
                WHERE
                    {field}='{value}'
                """
            )
        ).fetchone()

        if data is None:
            raise RecordDoesNotExistError(f"No record with {field} of {value} exists")

        return tuple(data)

    async def _get_many_by_field(self, field: str, value: str | int | bool | float) -> list[tuple]:
        """Gets many record by a given field.

        :param field: The field to match the value of
        :param value: The value to match
        :return: The records
        :raises RecordDoesNotExistError: If no record matches the value of the given field
        """

        data = await (
            await self._execute_query(
                f"""
                SELECT *
                FROM {self._table}
                WHERE
                    {field}='{value}'
                """
            )
        ).fetchall()
        # TODO: The above should really be a fetchmany() with a limit. This can be a future thing

        if not data:
            raise RecordDoesNotExistError(f"No record with {field} of {value} exists")

        return [tuple(item) for item in data]

    async def _add_record(self, data: dict) -> tuple:
        """Adds a record to the database

        :param data: The data to add
        :return: The data in the database
        """

        row_id = await self._database.execute_insert(
            f"""
            INSERT INTO {self._table}
            VALUES (
            \t{('\n\t'.join(['"' + str(value) + '",' for value in data.values()])).strip(',')}
            )
            """
        )

        await self._database.commit()

        data = await self._get_record_by_id(row_id[0])

        if data is None:
            raise RecordDoesNotExistError(f"No record with an id of {row_id[0]} exists")

        return data

    async def _add_ck_record(self, data: dict, keys: dict[str, int]) -> tuple:
        """Adds a record to the database

        :param data: The data to add
        :return: The data in the database
        """

        row_id = await self._database.execute_insert(
            f"""
            INSERT INTO {self._table}
            VALUES (
            \t{('\n\t'.join(['"' + str(value) + '",' for value in data.values()])).strip(',')}
            )
            """
        )

        await self._database.commit()

        data = await self._get_record_by_ids(keys)

        if data is None:
            raise RecordDoesNotExistError(f"No record with an id of {row_id[0]} exists")

        return data

    async def _update_record(self, record_id: int, new_values: dict[str, Any]) -> tuple:
        """Updates a record in the database

        :param record_id: The ID of the record to update
        :param new_values: The data to update
        :return: The updated record
        """

        await self._database.execute(
            f"""
            UPDATE {self._table}
            SET 
                id={record_id},
                {'\n\t'.join(f"{key}='{value}'," for key, value in new_values.items()).strip(',')}
            WHERE
                id={record_id}
            """
        )
        await self._database.commit()

        return await self._get_record_by_id(record_id)

    async def _update_ck_record(self, keys: dict[str, int], new_values: dict[str, Any]) -> tuple:
        """Updates a record with a composite key in the database

        :param keys: The keys that make up the composite key
        :param new_values: The data to update
        :return: The updated record
        """

        await self._database.execute(
            f"""
            UPDATE {self._table}
            SET
                {'\n\t'.join(f"{key}='{value}'," for key, value in new_values.items()).strip(',')}
            WHERE (
                {'\n\t'.join(f"{key}='{value}' AND " for key, value in keys.items()).strip('AND ')}
            )
            """
        )
        await self._database.commit()

        return await self._get_record_by_ids(keys)

    async def _delete_record(self, record_id: int):
        """Deletes a record from the database

        :param record_id: The record ID to delete
        :return:
        :raises RecordStillExistsError: If the record could not be deleted
        """

        await self._database.execute(
            f"""
            DELETE FROM {self._table}
            WHERE
                id={record_id}
            """
        )

        await self._database.commit()

        try:
            await self._get_record_by_id(record_id)
        except RecordDoesNotExistError:
            # We want the record to no longer exist. If this does not get raised, then there is an issue!
            ...
        else:
            raise RecordStillExistsError(f"Cannot delete record with ID of {record_id}")

    async def _delete_ck_record(self, keys: dict[str:int]):
        """Deletes a CK record from the database

        :param keys: The keys that comprise the CK
        :return:
        :raises RecordStillExistsError: If the record could not be deleted
        """

        await self._database.execute(
            f"""
            DELETE FROM {self._table}
            WHERE (
                {'\n\t'.join(f"{key}='{value}' AND " for key, value in keys.items()).strip('AND ')}
            )
            """
        )

        await self._database.commit()

        try:
            await self._get_record_by_ids(keys)
        except RecordDoesNotExistError:
            # We want the record to no longer exist. If this does not get raised, then there is an issue!
            ...
        else:
            raise RecordStillExistsError(f"Cannot delete record with CK of {keys}")

    @abstractmethod
    async def _add_default_records(self):
        """Adds the default records to the database if it has just created them

        :return:
        """

    async def __generate_table_columns_string(self) -> str:
        """Generates the string for the table columns

        :return: The string for the table columns
        """

        has_primary_key = False
        foreign_keys = []

        output_string = ""
        for column in self._table_columns:
            # Column name
            output_string += "\n\t"
            output_string += column.name

            # Column Datatype
            output_string += "\n\t\t"
            output_string += column.type

            if not column.can_be_null:
                output_string += "\n\t\t\t"
                output_string += "NOT NULL"

            # If the column is a primary key, add in the bits relevant to that
            if column.is_primary_key:
                output_string += "\n\t\t"
                output_string += f"CONSTRAINT {self._table}_pk"
                output_string += "\n\t\t\t"
                output_string += "PRIMARY KEY"
                has_primary_key = True

            elif column.foreign_key_table is not None:
                output_string += "\n\t\t"
                output_string += f"CONSTRAINT {self._table}_{column.name}_"
                if column.foreign_key_column is not None:
                    output_string += f"{column.foreign_key_column}_"
                output_string += "fk"

                output_string += "\n\t\t\t"
                output_string += f"REFERENCES {column.foreign_key_table}"
                if column.foreign_key_column is not None:
                    output_string += f" ({column.foreign_key_column})"

                foreign_keys.append(column.name)

            elif column.is_unique:
                output_string += "\n\t\t"
                output_string += f"CONSTRAINT {self._table}_{column.name}_unique"
                output_string += "\n\t\t\t"
                output_string += "unique"

            output_string += ","

        if not has_primary_key and foreign_keys:
            output_string += "\n\t"
            output_string += f"CONSTRAINT {self._table}_pk"
            output_string += "\n\t\t"
            output_string += f"PRIMARY KEY ({','.join(foreign_keys).strip(',')})"

        return output_string.removesuffix(",") + "\n"

    def __new__(cls, table: Table = ""):
        """Creates a new instance of this database if an instance doesn't already exist

        This overrides the default behaviour of the __new__() method, allowing a singleton pattern.
        If this is the first time instantiating a connection to the database, it will create a new instance of that
        class. However, if the same class is instantiated again, instead of creating a new object, it will return the
        same object as the first instantiation.
        Despite this being in the base class, this will allow each inherited class to be instantiated once with no
        conflicts between them.

        The first instance MUST have the table name. Any subsequent instance can have nothing for the table name.
        :param table: The name of the table in the database
        """
        if not cls.__instance:
            print(f"Instantiating a new {cls.__name__}")
            cls.__instance = super(DatabaseAdapter, cls).__new__(cls)

            if table != "":
                cls._table = table

        return cls.__instance
