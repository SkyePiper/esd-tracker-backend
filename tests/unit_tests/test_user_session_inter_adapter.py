"""Tests the users session inter adapter"""

from typing import Final

import pytest

from common.database.base_database.database_errors import (
    RecordDoesNotExistError,
)
from common.database.user_session_inter_database.user_session_inter_models import (
    UserSessionInterModel,
    UserSessionInterUpdateModel,
)
from common.enums.user_session_attendance import Attendance

USER_KEY: Final[str] = "user_id"
"""The key for the user id"""
SESSION_KEY: Final[str] = "training_session_id"
"""The key for the training session id"""


async def test_get_record_by_ids_valid_ids(new_user_session_inter_adapter):
    """Tests getting a record by its ID

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_user_session_inter_adapter.add_ck_record(
        UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED),
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    record = await new_user_session_inter_adapter.get_record_by_ids({USER_KEY: 0, SESSION_KEY: 0})

    assert record.user_attendance_type == Attendance.ATTENDED


async def test_get_record_by_ids_invalid_ids(new_user_session_inter_adapter):
    """Tests attempting to get a record by its ID

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    with pytest.raises(RecordDoesNotExistError):
        await new_user_session_inter_adapter.get_record_by_ids({USER_KEY: 100, SESSION_KEY: 100})


async def test_get_record_by_user_id_valid_ids(new_user_session_inter_adapter):
    """Tests getting a record by its ID

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_user_session_inter_adapter.add_ck_record(
        UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED),
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    records = await new_user_session_inter_adapter.get_all_records_with_user_id(0)
    assert len(records) == 1


async def test_get_record_by_user_id_invalid_ids(new_user_session_inter_adapter):
    """Tests getting a record by its ID

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_user_session_inter_adapter.add_ck_record(
        UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED),
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    with pytest.raises(RecordDoesNotExistError):
        await new_user_session_inter_adapter.get_all_records_with_user_id(100)


async def test_get_record_by_session_id_valid_ids(new_user_session_inter_adapter):
    """Tests getting a record by its ID

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_user_session_inter_adapter.add_ck_record(
        UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED),
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    records = await new_user_session_inter_adapter.get_all_records_with_user_id(0)
    assert len(records) == 1


async def test_get_record_by_session_id_invalid_ids(new_user_session_inter_adapter):
    """Tests getting a record by its ID

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_user_session_inter_adapter.add_ck_record(
        UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED),
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    with pytest.raises(RecordDoesNotExistError):
        await new_user_session_inter_adapter.get_all_records_with_session_id(100)


async def test_add_record(new_user_session_inter_adapter):
    """Tests adding a record

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    record = UserSessionInterModel(user_id=5, training_session_id=5, user_attendance_type=Attendance.ATTENDED)

    created_record = await new_user_session_inter_adapter.add_ck_record(
        record, {USER_KEY: record.user_id, SESSION_KEY: record.training_session_id}
    )

    assert record == created_record


async def test_update_record_valid_ids(new_user_session_inter_adapter):
    """Tests updating a record

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_user_session_inter_adapter.add_ck_record(
        UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED),
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    record_updates = UserSessionInterUpdateModel(user_attendance_type=Attendance.NO_LONGER_ATTENDING)

    updated_record = await new_user_session_inter_adapter.update_ck_record(
        record_updates, {USER_KEY: 0, SESSION_KEY: 0}
    )

    updated_record_data = updated_record.model_dump()
    for key, value in {key: value for key, value in record_updates.model_dump().items() if value is not None}.items():
        assert updated_record_data[key] == value


async def test_update_record_invalid_ids(new_user_session_inter_adapter):
    """Tests attempting to update a record with an invalid id

    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    record_updates = UserSessionInterUpdateModel(user_attendance_type=Attendance.NO_SHOW)

    with pytest.raises(RecordDoesNotExistError):
        await new_user_session_inter_adapter.update_ck_record(record_updates, keys={USER_KEY: 0, SESSION_KEY: 0})
