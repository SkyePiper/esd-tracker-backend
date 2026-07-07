"""Configures the tests"""

from pathlib import Path
from typing import Any, AsyncGenerator, Final

import pytest
from dotenv import load_dotenv

from common.database.training_session_database.training_session_database_adaptor import (
    TrainingSessionDatabaseAdaptor,
)
from common.database.training_session_database.training_session_database_controller import (
    TrainingSessionController,
)
from common.database.user_database.user_database_adaptor import UserDatabaseAdaptor
from common.database.user_database.user_database_controller import UserController
from common.database.user_database.user_models import UserModel
from common.database.user_session_inter_database.user_session_inter_database_adaptor import (
    UserSessionInterDatabaseAdapter,
)

__ENV_PATH: Final[Path] = Path(__file__).parent.joinpath(".env")
"""The path to the .env file"""
__DATABASE_PATH: Final[Path] = Path(__file__).parent.joinpath("esdTrackerDb.sqlite")
"""The path to the database file"""

load_dotenv(__ENV_PATH.absolute(), override=True)


@pytest.fixture(scope="function")
async def remove_database():
    """Removes the database, allowing for a new database to be created

    :return:
    """

    __DATABASE_PATH.unlink(missing_ok=True)


@pytest.fixture
async def new_users_adapter(remove_database) -> AsyncGenerator[UserDatabaseAdaptor, Any]:
    """Creates a new users adapter

    :param remove_database:
    :return: The users adapter
    """
    adapter = UserDatabaseAdaptor()

    # Update the database path to the test one
    setattr(UserDatabaseAdaptor, "_DatabaseAdapter__database_path", __DATABASE_PATH)

    await adapter.load_db()

    yield adapter

    await adapter.disconnect()


@pytest.fixture
async def new_users_controller(new_users_adapter) -> AsyncGenerator[UserController, Any]:
    """Creates a new users controller

    :param new_users_adapter: The new users adapter
    :return: The users controller
    """

    controller = UserController()

    yield controller


@pytest.fixture
async def new_training_session_adapter(remove_database) -> AsyncGenerator[TrainingSessionDatabaseAdaptor, Any]:
    """Creates a new training session adapter

    :param remove_database:
    :return: The training session adapter
    """

    adapter = TrainingSessionDatabaseAdaptor()

    # Update the database path to the test one
    setattr(TrainingSessionDatabaseAdaptor, "_DatabaseAdapter__database_path", __DATABASE_PATH)

    await adapter.load_db()

    yield adapter

    await adapter.disconnect()


@pytest.fixture
async def new_training_session_controller(
    new_training_session_adapter,
    new_users_adapter,
) -> AsyncGenerator[TrainingSessionController, Any]:
    """Creates a new training session controller

    :param new_training_session_adapter: The new training session adapter
    :param new_users_adapter: The new users adapter
    :return: The training session controller
    """

    controller = TrainingSessionController()

    yield controller


@pytest.fixture
async def new_user_session_inter_adapter(remove_database) -> AsyncGenerator[UserSessionInterDatabaseAdapter, Any]:
    """Creates a new user session inter adapter

    :param remove_database:
    :return: The user session inter adapter
    """

    adapter = UserSessionInterDatabaseAdapter()

    # Update the database path to the test one
    setattr(adapter, "_DatabaseAdapter__database_path", __DATABASE_PATH)

    await adapter.load_db()

    yield adapter

    print("Disconnected")

    await adapter.disconnect()


@pytest.fixture
async def admin_user(new_users_adapter) -> UserModel:
    """Gets the admin user from the users database

    :param new_users_adapter: The users adapter
    :return: The admin user
    """

    return await new_users_adapter.get_record_by_id(0)


@pytest.fixture
async def default_user(new_users_adapter) -> UserModel:
    """Gets the default user from the users database

    :param new_users_adapter: The users adapter
    :return: The default user
    """

    return await new_users_adapter.get_record_by_id(1)
