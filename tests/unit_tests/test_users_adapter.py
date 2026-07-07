"""Tests the users adapter"""

from os import getenv

import pytest

from common.auth.password_utils import hash_password, verify_password
from common.database.base_database.database_errors import (
    RecordDoesNotExistError,
    RecordStillExistsError,
)
from common.database.user_database.user_models import UserModel, UserUpdateModel


async def test_get_all_records(new_users_adapter):
    """Tests getting all the records

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    assert len(await new_users_adapter.get_all_records()) == 2


async def test_get_record_by_id_valid_id(new_users_adapter):
    """Tests getting a record by its ID

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    record = await new_users_adapter.get_record_by_id(0)

    assert record.forename == "Admin"
    assert record.surname == "Admin"
    assert record.email == getenv("ADMIN_EMAIL")
    assert record.permissions == 1
    assert await verify_password(getenv("ADMIN_PASSWORD"), record.password)


async def test_get_record_by_id_invalid_id(new_users_adapter):
    """Tests attempting to get a record by its ID

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    with pytest.raises(RecordDoesNotExistError):
        await new_users_adapter.get_record_by_id(100)


async def test_get_record_by_email_valid_email(new_users_adapter):
    """Tests getting a record by its email

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    record = await new_users_adapter.get_record_by_email(getenv("ADMIN_EMAIL"))

    assert record.forename == "Admin"
    assert record.surname == "Admin"
    assert record.email == getenv("ADMIN_EMAIL")
    assert record.permissions == 1
    assert await verify_password(getenv("ADMIN_PASSWORD"), record.password)


async def test_get_record_by_email_invalid_email(new_users_adapter):
    """Tests attempting to get a record by its email

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    with pytest.raises(RecordDoesNotExistError):
        await new_users_adapter.get_record_by_email("this.email.doesnt@exist.com")


async def test_add_record(new_users_adapter):
    """Tests adding a record

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    record = UserModel(
        id=5,
        forename="Test",
        surname="User",
        email="test@user.come",
        permissions=1,
        password=await hash_password("abc"),
    )

    created_record = await new_users_adapter.add_record(record)

    assert record == created_record


async def test_update_record_valid_id(new_users_adapter):
    """Tests updating a record

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    record_updates = UserUpdateModel(
        forename="Test",
        surname="Update",
        email="test@update.com",
    )

    updated_record = await new_users_adapter.update_record(0, record_updates)

    updated_record_data = updated_record.model_dump()
    for key, value in {key: value for key, value in record_updates.model_dump().items() if value is not None}.items():
        assert updated_record_data[key] == value


async def test_update_record_invalid_id(new_users_adapter):
    """Tests attempting to update a record with an invalid id

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    record_updates = UserUpdateModel(
        forename="Test",
        surname="Update",
        email="test@update.com",
    )

    with pytest.raises(RecordDoesNotExistError):
        await new_users_adapter.update_record(100, record_updates)


async def test_delete_record_valid_id(new_users_adapter):
    """Tests deleting a record with a valid id

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    await new_users_adapter.delete_record(1)

    assert await new_users_adapter.get_count() == 1


async def test_delete_record_admin_id(new_users_adapter):
    """Tests attempting to delete the admin user

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    with pytest.raises(RecordStillExistsError):
        await new_users_adapter.delete_record(0)


async def test_delete_record_invalid_id(new_users_adapter):
    """Tests attempting to delete a record with an invalid id

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    await new_users_adapter.delete_record(100)
    assert await new_users_adapter.get_count() == 2
