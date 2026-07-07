"""Tests the user controller"""

import pytest

from common.auth.password_utils import verify_password
from common.database.base_database.database_errors import RecordStillExistsError
from common.database.user_database.user_models import UserModel, UserUpdateModel
from common.enums.permissions import Permissions
from common.helper_functions.errors import UnauthorisedError, WeakPasswordError


async def test_get_all_records_admin(new_users_controller, admin_user):
    """Tests getting all the records with the admin user

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :return:
    """

    users = await new_users_controller.get_all_records(admin_user)
    assert len(users) == 2


async def test_get_all_records_default(new_users_controller, default_user):
    """Tests getting all the records with the default user

    :param new_users_controller: The users controller for this test
    :param default_user: The default user
    :return:
    """

    with pytest.raises(UnauthorisedError):
        await new_users_controller.get_all_records(default_user)


async def test_get_record_by_id_admin(new_users_controller, admin_user):
    """Tests getting a record by its id with the admin user

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :return:
    """

    user = await new_users_controller.get_record_by_id(admin_user, 0)
    assert user == admin_user


async def test_get_record_by_id_default(new_users_controller, default_user):
    """Tests getting a record by its id with the default user

    :param new_users_controller: The users controller for this test
    :param default_user: The default user
    :return:
    """

    with pytest.raises(UnauthorisedError):
        await new_users_controller.get_record_by_id(default_user, 0)


async def test_add_record_admin(new_users_controller, admin_user):
    """Tests adding a user with the admin user

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :return:
    """

    password = "ThisPasswordIsMoreThan12CharactersLong!"
    user = UserModel(
        id=5,
        forename="Test",
        surname="User",
        email="test@user.com",
        permissions=Permissions.ADMINISTER,
        password=password,
    )

    created_user = await new_users_controller.add_record(admin_user, user)

    assert created_user.forename == user.forename
    assert created_user.surname == user.surname
    assert created_user.email == user.email
    assert created_user.permissions == user.permissions
    assert await verify_password(password, created_user.password)


async def test_add_record_default(new_users_controller, default_user):
    """Tests adding a user with the default user

    :param new_users_controller: The users controller for this test
    :param default_user: The default user
    :return:
    """

    user = UserModel(
        id=5,
        forename="Test",
        surname="User",
        email="test@user.com",
        permissions=Permissions.ADMINISTER,
        password="ThisPasswordIsMoreThan12CharactersLong!",
    )

    with pytest.raises(UnauthorisedError):
        await new_users_controller.add_record(default_user, user)


@pytest.mark.parametrize("password", ["a", "aaaaaaaaaaaa", "AAAAAAAAAAAA", "AaAaAaAaAaAa", "012345678910"])
async def test_add_user_weak_password(new_users_controller, admin_user, password):
    """Tests adding a user with a weak password

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :param password: The password for the test
    :return:
    """

    user = UserModel(
        id=5,
        forename="Test",
        surname="User",
        email="test@user.com",
        permissions=Permissions.ADMINISTER,
        password=password,
    )

    with pytest.raises(WeakPasswordError):
        await new_users_controller.add_record(admin_user, user)


async def test_update_record_admin(new_users_controller, admin_user):
    """Tests updating a record with the admin user

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :return:
    """

    record_updates = UserUpdateModel(
        forename="Test",
        surname="Update",
        email="a@b.com",
    )

    # Own User
    updated_record = await new_users_controller.update_record(admin_user, 0, record_updates)

    updated_record_data = updated_record.model_dump()
    for key, value in {key: value for key, value in record_updates.model_dump().items() if value is not None}.items():
        assert updated_record_data[key] == value

    # Different User
    record_updates.email = "b@a.com"
    updated_record = await new_users_controller.update_record(admin_user, 1, record_updates)

    updated_record_data = updated_record.model_dump()
    for key, value in {key: value for key, value in record_updates.model_dump().items() if value is not None}.items():
        assert updated_record_data[key] == value


async def test_update_record_default(new_users_controller, default_user):
    """Tests updating a record with the default user

    :param new_users_controller: The users controller for this test
    :param default_user: The default user
    :return:
    """

    record_updates = UserUpdateModel(
        forename="Test",
        surname="Update",
        email="test@update.com",
    )

    # Own User
    with pytest.raises(UnauthorisedError):
        await new_users_controller.update_record(default_user, 1, record_updates)

    # Different User
    with pytest.raises(UnauthorisedError):
        await new_users_controller.update_record(default_user, 0, record_updates)


async def test_delete_record_admin(new_users_controller, admin_user):
    """Tests deleting a record with the admin user

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :return:
    """

    await new_users_controller.delete_record(admin_user, 1)
    assert len(await new_users_controller.get_all_records(admin_user)) == 1


async def test_delete_admin_record_admin(new_users_controller, admin_user):
    """Tests deleting the admin record with the admin user

    :param new_users_controller: The users controller for this test
    :param admin_user: The admin user
    :return:
    """

    with pytest.raises(RecordStillExistsError):
        await new_users_controller.delete_record(admin_user, 0)


async def test_delete_record_default(new_users_controller, default_user):
    """Tests deleting a record with the default user

    :param new_users_controller: The users controller for this test
    :param default_user: The default user
    :return:
    """

    with pytest.raises(UnauthorisedError):
        await new_users_controller.delete_record(default_user, 1)
