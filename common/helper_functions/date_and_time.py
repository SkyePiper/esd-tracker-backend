"""Helper functions regarding the date and time"""

from datetime import UTC, datetime, timedelta
from os import getenv

from common.helper_functions.errors import InvalidDatetimeFormatError
from dotenv import load_dotenv

load_dotenv()

__JTW_TIMEOUT = float(getenv("JWT_EXPIRE_MINUTES"))


def get_utc_time_now() -> datetime:
    """Gets the current time at UCT 0

    :return: The current datetime
    """

    return datetime.now(UTC)


def get_string_datetime_now() -> str:
    """Gets the current UTC datetime in the string format

    :return: The string format of the current UTC time
    """

    return get_utc_time_now().replace(microsecond=0).isoformat()


def validate_datetime(datetime_to_validate: str) -> str:
    """Validates the give datetime

    :param datetime_to_validate: The datetime to validate
    :return: The validated datetime
    :raises InvalidDatetimeFormatError: If the datetime format is incorrect
    """

    try:
        return datetime.fromisoformat(datetime_to_validate).isoformat()
    except ValueError as e:
        raise InvalidDatetimeFormatError(message=f"Invalid datetime format: {datetime_to_validate}") from e


def validate_future_datetime(datetime_to_check: datetime) -> bool:
    """Checks whether a datetime is in the future

    :param datetime_to_check: The datetime to check
    :return: Whether the datetime is in the future
    """

    return datetime_to_check > get_utc_time_now()


def validate_future_datetime_from_string(datetime_to_check: str) -> bool:
    """Checks whether a iso-format datetime is in the future

    :param datetime_to_check: The datetime to check
    :return: Whether the datetime is in the future or not
    """

    return validate_future_datetime(datetime.fromisoformat(validate_datetime(datetime_to_check)))


def create_user_jwt_expiry_date() -> str:
    """Creates the expiry date for a User JWT

    :return: The expiry date
    """

    return (get_utc_time_now() + timedelta(minutes=__JTW_TIMEOUT)).isoformat()
