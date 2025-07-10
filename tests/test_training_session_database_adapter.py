"""Tests for the training session database adapter"""

from datetime import datetime
from sqlite3 import OperationalError
from typing import Any

import pytest
from dotenv import load_dotenv
from main import app
from pydantic import BaseModel, Field, ValidationError

load_dotenv(".env.tests", override=True)


from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase

from common.database.base_database.database_adapter import DatabaseAdapter
from common.database.training_session_database.training_session_database_adaptor import \
    TrainingSessionDatabaseAdaptor
from common.database.training_session_database.training_session_models import (
    TrainingSessionModel, TrainingSessionUpdateModel)
from common.helper_functions.date_and_time import get_string_datetime_now
from fastapi.testclient import TestClient


class InvalidTrainingSessionModel(TrainingSessionModel):
    """A model containing data which is invalid"""

    extra_field: Any = Field(...)


@pytest.mark.asyncio()
class TrainingSessionDatabaseAdapterTest(IsolatedAsyncioTestCase):
    """Tests for the training session database adapter"""

    adapter: TrainingSessionDatabaseAdaptor = None
    number_records: int = 0
    client: TestClient

    @classmethod
    def setUpClass(cls):
        """Sets up the test class

        :return:
        """

        cls.adapter = TrainingSessionDatabaseAdaptor()

        database_path = Path(f"./databases/{cls.__name__}.sqlite")

        # Create the database, overwriting the existing one if it exists
        database_path.parent.mkdir(parents=True, exist_ok=True)
        with open(database_path, "w"):
            ...

        # We can only set the database path if the UNIT_TESTS env var is set to TRUE
        cls.adapter.database_path = database_path

        # Assert that the database exists
        assert database_path.exists()
        assert cls.adapter.database_path == database_path

        cls.client = TestClient(app)

    @staticmethod
    def get_valid_datetimes() -> list[str]:
        """Gets a list of valid datetimes

        :return: A list of valid datetimes
        """

        return [
            "2025-06-25T02:05:45.666487+00:00",
            "2000-01-12T03:34:45.456789+01:00",
            "2123-06-25T02:05:45.666487-00:50",
        ]

    @staticmethod
    def get_invalid_datetimes() -> list[Any]:
        """Gets a list of invalid datetimes

        :return: A list of invalid datetimes
        """

        return [
            # "2025-06-25T02:05:45.666487",
            # "2025-06-25T02:05:45+0000",
            # "2025-06-2502:05:45.666487+0000",
            datetime.now(),
            True,
            1,
            2.3,
        ]

    def test_new_instance(self):
        """Tests making a new instance of the database adapter

        :return:
        """

        self.assertEqual(TrainingSessionDatabaseAdaptor(), self.adapter)

    # We need this test to go first as this will make the cursor object which is used by most other things in the
    # database adapters.
    @pytest.mark.asyncio()
    @pytest.mark.order(0)
    async def test_create_table(self):
        """Tests that the table gets correctly created

        :return:
        """

        await self.adapter.load_db()
        self.assertIsNotNone(self.adapter._cursor, msg="Failed to create the table")

    @pytest.mark.asyncio()
    async def test_get_next_id(self):
        """Tests the get_next_id function

        :return:
        """

        self.number_records = await self.adapter.get_count()
        if self.number_records == 0:
            # If there are no records, then we need to set the number_records to -1 to allow +1 logic to work later
            self.number_records = -1

        self.assertEqual(await self.adapter.get_next_id(), self.number_records)

    @pytest.mark.asyncio()
    async def test_add_records_valid_data(self):
        """Tests adding a record to the database

        :return:
        """

        for item in self.get_valid_datetimes():
            with self.subTest(msg=f"Failed test using a datetime value of {item}", item=item):
                model = TrainingSessionModel(
                    id=await self.adapter.get_next_id(), created=get_string_datetime_now(), datetime=item
                )

                record = await self.adapter.add_record(model)
                self.assertEqual(
                    record.id,
                    self.number_records,
                    msg=f"Record ID is not as expected: Record ID: {record.id}; Expected: {self.number_records}",
                )

                self.number_records += 1
                record_count = await self.adapter.get_count()
                self.assertEqual(
                    record_count,
                    self.number_records,
                    msg=f"Record count is not as expected: Record count: {record_count}; Expected: {self.number_records}",
                )

    @pytest.mark.asyncio()
    async def test_add_records_invalid_model(self):
        """Tests attempting to add a incorrect value to the model

        :return:
        """

        for item in self.get_invalid_datetimes():
            with self.subTest(item=item):
                with self.assertRaises(ValidationError):
                    TrainingSessionModel(
                        id=await self.adapter.get_next_id(), created=get_string_datetime_now(), datetime=item
                    )

    @pytest.mark.asyncio()
    async def test_add_records_invalid_data(self):
        """Tests attempting to add invalid data to the database

        :return:
        """

        models = [
            InvalidTrainingSessionModel(
                id=0,
                created=get_string_datetime_now(),
                datetime=get_string_datetime_now(),
                extra_field="This should raise an error",
            ),
        ]

        print(f"Attempting to add {len(models)} invalid models to the database")

        for invalid_model in models:
            with self.subTest(
                f"Failed test using the current model: {invalid_model.model_dump_json(indent=2)}",
                invalid_model=invalid_model,
            ):
                with self.assertRaises(OperationalError):
                    await self.adapter.add_record(invalid_model)
