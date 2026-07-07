"""Tests the training session controller"""

from typing import Final

import pytest

from common.auth.password_utils import verify_password
from common.database.base_database.database_errors import RecordStillExistsError
from common.database.training_session_database.training_session_models import (
    TrainingSessionModel,
    TrainingSessionUpdateModel,
)
from common.database.user_database.user_models import UserModel, UserUpdateModel
from common.database.user_session_inter_database.user_session_inter_models import (
    UserSessionInterModel,
)
from common.enums.permissions import Permissions
from common.enums.user_session_attendance import Attendance
from common.helper_functions.date_and_time import get_string_datetime_now
from common.helper_functions.errors import UnauthorisedError, WeakPasswordError

USER_KEY: Final[str] = "user_id"
"""The key for the user id"""
SESSION_KEY: Final[str] = "training_session_id"
"""The key for the training session id"""


async def test_get_all_records_admin(new_training_session_controller, admin_user):
    """Tests getting all the records with the admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user
    :return:
    """

    users = await new_training_session_controller.get_all_records(admin_user)
    assert len(users) == 0


async def test_get_all_records_default(new_training_session_controller, default_user):
    """Tests getting all the records with the default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user
    :return:
    """

    # Update the default users permissions to not include the GET_TRAINING_SESSION permission
    default_user.permissions = 0

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.get_all_records(default_user)


async def test_get_record_by_id_admin(new_training_session_controller, admin_user):
    """Tests getting a record by its id with the admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    session = TrainingSessionModel(id=0)
    await new_training_session_controller.add_record(admin_user, session)

    record = await new_training_session_controller.get_record_by_id(admin_user, 0)
    assert record == session


async def test_get_record_by_id_default(new_training_session_controller, default_user):
    """Tests getting a record by its id with the default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user
    :return:
    """

    # Update the default users permissions to not include the GET_TRAINING_SESSION permission
    default_user.permissions = 0

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.get_record_by_id(default_user, 0)


async def test_add_record_admin(new_training_session_controller, admin_user):
    """Tests adding a user with the admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    session = TrainingSessionModel(id=0)
    new_session = await new_training_session_controller.add_record(admin_user, session)

    assert new_session == session


async def test_add_record_default(new_training_session_controller, default_user):
    """Tests adding a user with the default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user
    :return:
    """

    session = TrainingSessionModel(id=0)

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.add_record(default_user, session)


async def test_get_user_attendance_admin(new_training_session_controller, new_user_session_inter_adapter, admin_user):
    """Tests getting the user attendance with an admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user
    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    assert await new_training_session_controller.get_user_attendance(admin_user, 0) == []

    # There are no records in the database by default. Add one before performing the main part of the test
    attendance = UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED)
    await new_user_session_inter_adapter.add_ck_record(
        attendance,
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    assert (await new_training_session_controller.get_user_attendance(admin_user, 0))[0] == attendance


async def test_get_user_attendance_default(
    new_training_session_controller, default_user, new_user_session_inter_adapter
):
    """Tests getting the user attendance with a default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user
    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # Update the default users permissions to not include the GET_TRAINING_SESSION permission
    default_user.permissions = 0

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.get_user_attendance(default_user, 0)

    # There are no records in the database by default. Add one before performing the main part of the test
    attendance = UserSessionInterModel(user_id=0, training_session_id=0, user_attendance_type=Attendance.ATTENDED)
    await new_user_session_inter_adapter.add_ck_record(
        attendance,
        keys={USER_KEY: 0, SESSION_KEY: 0},
    )

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.get_user_attendance(default_user, 0)


async def test_mark_user_attendance_admin(new_training_session_controller, new_user_session_inter_adapter, admin_user):
    """Tests marking the users attendance with the admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user for this test
    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_training_session_controller.add_record(admin_user, TrainingSessionModel(id=0))

    attendance_record = await new_training_session_controller.mark_user_attendance(
        admin_user, 0, admin_user.email, Attendance.SIGNED_UP
    )
    assert attendance_record.user_id == 0
    assert attendance_record.training_session_id == 0
    assert attendance_record.user_attendance_type == Attendance.SIGNED_UP

    attendance_record = await new_training_session_controller.mark_user_attendance(
        admin_user, 0, admin_user.email, Attendance.ATTENDED
    )
    assert attendance_record.user_id == 0
    assert attendance_record.training_session_id == 0
    assert attendance_record.user_attendance_type == Attendance.ATTENDED


async def test_mark_user_attendance_default(
    new_training_session_controller, default_user, new_user_session_inter_adapter
):
    """Tests marking the users attendance with the default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user for this test
    :param new_user_session_inter_adapter: The user session inter adapter for this test
    :return:
    """

    # Update the default users permissions to not include the GET_TRAINING_SESSION permission
    default_user.permissions = Permissions.CREATE_TRAINING_SESSION

    # There are no records in the database by default. Add one before performing the main part of the test
    await new_training_session_controller.add_record(default_user, TrainingSessionModel(id=0))

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.mark_user_attendance(
            default_user, 0, default_user.email, Attendance.SIGNED_UP
        )

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.mark_user_attendance(
            default_user, 0, default_user.email, Attendance.ATTENDED
        )


async def test_update_record_admin(new_training_session_controller, admin_user):
    """Tests updating a record with the admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    session = TrainingSessionModel(id=0)
    await new_training_session_controller.add_record(admin_user, session)

    record_updates = TrainingSessionUpdateModel(datetime=get_string_datetime_now())

    updated_record = await new_training_session_controller.update_record(admin_user, 0, record_updates)

    updated_record_data = updated_record.model_dump()
    for key, value in {key: value for key, value in record_updates.model_dump().items() if value is not None}.items():
        assert updated_record_data[key] == value


async def test_update_record_default(new_training_session_controller, default_user):
    """Tests updating a record with the default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user
    :return:
    """

    record_updates = TrainingSessionUpdateModel(datetime=get_string_datetime_now())

    # Own User
    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.update_record(default_user, 0, record_updates)


async def test_delete_record_admin(new_training_session_controller, admin_user):
    """Tests deleting a record with the admin user

    :param new_training_session_controller: The training session controller for this test
    :param admin_user: The admin user
    :return:
    """

    # There are no records in the database by default. Add one before performing the main part of the test
    session = TrainingSessionModel(id=0)
    await new_training_session_controller.add_record(admin_user, session)

    await new_training_session_controller.delete_record(admin_user, 0)
    assert len(await new_training_session_controller.get_all_records(admin_user)) == 0


async def test_delete_record_default(new_training_session_controller, default_user):
    """Tests deleting a record with the default user

    :param new_training_session_controller: The training session controller for this test
    :param default_user: The default user
    :return:
    """

    with pytest.raises(UnauthorisedError):
        await new_training_session_controller.delete_record(default_user, 0)
