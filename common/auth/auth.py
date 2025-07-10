"""Functions relating to the authentication of a user"""

from asyncio import sleep
from os import getenv, urandom
from typing import Annotated

from common.auth.auth_errors import AuthTimeoutError, InvalidAuthError
from common.auth.auth_models import JwtModel, UserJwtDataModel
from common.auth.password_utils import verify_password
from common.database.base_database.database_errors import RecordDoesNotExistError
from common.database.user_database.user_database_adaptor import UserDatabaseAdaptor
from common.database.user_database.user_models import UserModel
from common.helper_functions.date_and_time import get_utc_time_now, validate_future_datetime_from_string
from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError, decode, encode

load_dotenv()

__JWT_SECRET = getenv("JWT_SECRET")
__JWT_ALGORITHM = getenv("JWT_ALGORITHM")
__JTW_TIMEOUT = float(getenv("JWT_EXPIRE_MINUTES"))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
user_adaptor = UserDatabaseAdaptor()


async def authenticate_user_by_email_password(email: str, password: str) -> UserModel:
    """Authenticates a user by their email and their password

    :param email: The email of the user
    :param password: The password of the user
    :return: The user
    :raises InvalidAuthError: If the user doesn't exist
    """

    try:
        user = await user_adaptor.get_record_by_email(email)

        await sleep(1 / int(urandom(1).hex(), base=16))

        if not await verify_password(password, user.password):
            raise InvalidAuthError()

    except RecordDoesNotExistError as e:
        # Add a random amount of sleep time to help prevent timing attacks
        await sleep(1 / int(urandom(1).hex(), base=16))

        raise InvalidAuthError() from e

    # Add a random amount of sleep time to help prevent timing attacks
    await sleep(1 / int(urandom(1).hex(), base=16))

    return user


async def create_access_token(data: UserJwtDataModel) -> str:
    """Creates a JWT

    :param data: The data to go into the JWT
    :return: The JWT
    """

    token = encode(data.model_dump(), __JWT_SECRET, __JWT_ALGORITHM)
    return token


async def get_user_from_jwt(token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    """Gets a user from a JWT

    :param token: The JWT
    :return: The User
    :raises UnauthorisedError
    """

    try:
        payload = UserJwtDataModel(**decode(token, __JWT_SECRET, algorithms=[__JWT_ALGORITHM]))
    except InvalidTokenError as e:
        raise InvalidAuthError() from e

    if not validate_future_datetime_from_string(payload.expires):
        raise AuthTimeoutError()

    return await user_adaptor.get_record_by_id(payload.user_id)


async def create_user_jwt(user: UserModel) -> JwtModel:
    """Creates a JWT for a user

    :param user: The user
    :return: The JWT
    """

    # Make sure the user is valid
    await user_adaptor.get_record_by_id(user.id)
    user_jwt = UserJwtDataModel(
        user_id=user.id,
        permissions=user.permissions,
        user_forename=user.forename,
        user_surname=user.surname,
        user_email=user.email,
    )

    return JwtModel(access_token=await create_access_token(user_jwt), token_type="bearer", data=user_jwt.model_dump())


VALIDATE_USER = Annotated[UserModel, Depends(get_user_from_jwt)]
