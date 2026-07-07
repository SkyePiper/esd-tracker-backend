"""Tests for the authentication"""

from datetime import UTC, datetime, timedelta
from os import getenv
from pathlib import Path
from typing import Final

import pytest
from dotenv import load_dotenv

from common.auth.auth_errors import AuthTimeoutError, InvalidAuthError
from common.auth.auth_models import UserJwtDataModel

__ENV_PATH: Final[Path] = Path(__file__).parent.parent.joinpath(".env")
"""The path to the .env file"""

load_dotenv(__ENV_PATH.absolute(), override=True)

from common.auth.auth import (
    authenticate_user_by_email_password,
    create_access_token,
    create_user_jwt,
    get_user_from_jwt,
)


async def test_authenticate_user_by_email_password_valid(admin_user):
    """Tests authenticating a user with a valid username and password

    :param admin_user: The admin user
    :return:
    """

    user = await authenticate_user_by_email_password(getenv("ADMIN_EMAIL"), getenv("ADMIN_PASSWORD"))
    assert user == admin_user


async def test_authenticate_user_by_email_password_invalid(new_users_adapter):
    """Tests attempting to authenticate a user with an invalid email or password

    :param new_users_adapter: The users adapter for this test
    :return:
    """

    with pytest.raises(InvalidAuthError):
        await authenticate_user_by_email_password("a", "b")
    with pytest.raises(InvalidAuthError):
        await authenticate_user_by_email_password(getenv("ADMIN_EMAIL"), "b")


async def test_validate_jwt(admin_user):
    """Tests the creation and validation of a java web token

    :param admin_user: The admin user
    :return:
    """

    token = await create_user_jwt(admin_user)

    assert await get_user_from_jwt(token.access_token) == admin_user


async def test_validate_jwt_invalid_token():
    """Tests attempting to decode a invalid jwt

    :return:
    """

    with pytest.raises(InvalidAuthError):
        await get_user_from_jwt("auohduaohdwnadwahdfbnawouhanbfoiybasjbnad")

    token = await create_access_token(
        UserJwtDataModel(
            user_id=0,
            user_forename="a",
            user_surname="b",
            user_email="a@b.com",
            permissions=0,
            expires=(datetime.now(UTC) + timedelta(minutes=-1)).isoformat(),
        )
    )

    with pytest.raises(AuthTimeoutError):
        await get_user_from_jwt(token)
