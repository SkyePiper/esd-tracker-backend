"""Tests the training session adapter"""

import pytest

from common.database.base_database.database_errors import (
    RecordDoesNotExistError,
)
from common.database.training_session_database.training_session_models import (
    TrainingSessionModel,
    TrainingSessionUpdateModel,
)
from common.helper_functions.date_and_time import get_string_datetime_now


async def test_get_all_records(new_training_session_adapter):
    """Tests getting all the records

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    assert len(await new_training_session_adapter.get_all_records()) == 0


async def test_get_record_by_id_valid_id(new_training_session_adapter):
    """Tests getting a record by its ID

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_training_session_adapter.add_record(TrainingSessionModel(id=0))

    record = await new_training_session_adapter.get_record_by_id(0)

    assert record.id == 0


async def test_get_record_by_id_invalid_id(new_training_session_adapter):
    """Tests attempting to get a record by its ID

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    with pytest.raises(RecordDoesNotExistError):
        await new_training_session_adapter.get_record_by_id(100)


async def test_add_record(new_training_session_adapter):
    """Tests adding a record

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    record = TrainingSessionModel(id=5)

    created_record = await new_training_session_adapter.add_record(record)

    assert record == created_record


async def test_update_record_valid_id(new_training_session_adapter):
    """Tests updating a record

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_training_session_adapter.add_record(TrainingSessionModel(id=0))

    record_updates = TrainingSessionUpdateModel(datetime=get_string_datetime_now())

    updated_record = await new_training_session_adapter.update_record(0, record_updates)

    updated_record_data = updated_record.model_dump()
    for key, value in {key: value for key, value in record_updates.model_dump().items() if value is not None}.items():
        assert updated_record_data[key] == value


async def test_update_record_invalid_id(new_training_session_adapter):
    """Tests attempting to update a record with an invalid id

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    record_updates = TrainingSessionUpdateModel(datetime=get_string_datetime_now())

    with pytest.raises(RecordDoesNotExistError):
        await new_training_session_adapter.update_record(100, record_updates)


async def test_delete_record_valid_id(new_training_session_adapter):
    """Tests deleting a record with a valid id

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    # There are no records in the database by default. Add two before performing the main part of the test
    await new_training_session_adapter.add_record(TrainingSessionModel(id=0))
    await new_training_session_adapter.add_record(TrainingSessionModel(id=1))

    await new_training_session_adapter.delete_record(0)

    assert await new_training_session_adapter.get_count() == 1


async def test_delete_record_invalid_id(new_training_session_adapter):
    """Tests attempting to delete a record with an invalid id

    :param new_training_session_adapter: The training session adapter for this test
    :return:
    """

    # There are no records in the database by default. Add two before performing the main part of the test
    await new_training_session_adapter.add_record(TrainingSessionModel(id=0))
    await new_training_session_adapter.add_record(TrainingSessionModel(id=1))

    await new_training_session_adapter.delete_record(100)
    assert await new_training_session_adapter.get_count() == 2
