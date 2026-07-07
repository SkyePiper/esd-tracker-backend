"""Unit tests for the datetime functions"""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

import pytest
from dotenv import load_dotenv
from pytest import approx

__ENV_PATH: Final[Path] = Path(__file__).parent.joinpath(".env")
"""The path to the .env file"""
load_dotenv(__ENV_PATH.absolute(), override=True)

from common.helper_functions.date_and_time import (
    __JWT_TIMEOUT,
    create_user_jwt_expiry_date,
    get_string_datetime_now,
    get_utc_time_now,
    validate_datetime,
    validate_future_datetime,
    validate_future_datetime_from_string,
)
from common.helper_functions.errors import InvalidDatetimeFormatError


def test_get_datetime_now():
    """Tests the get_datetime_now() function

    :return:
    """

    now = get_utc_time_now()
    comparison = datetime.now(UTC)

    print(
        f"\n"
        f"Function datetime: {now}; Comparison Datetime: {comparison};\n"
        f"Now timestamp: {now.timestamp()}; Comparison Timestamp: {comparison.timestamp()};\n"
        f"Approx value range: {approx(0.5, rel=10)}"
    )

    assert comparison.timestamp() - now.timestamp() == approx(0.5, rel=10)


def test_get_datetime_now_str():
    """Tests getting the current datetime as in the ISO 8601-1:2019 format

    :return:
    """

    now_datetime = datetime.now(UTC)
    now_str = get_string_datetime_now()

    print(f"\nDatetime String: {now_str}")

    datetime_from_str = datetime.fromisoformat(now_str)

    assert datetime_from_str.year == now_datetime.year
    assert datetime_from_str.month == now_datetime.month
    assert datetime_from_str.day == now_datetime.day
    assert datetime_from_str.hour == now_datetime.hour
    assert datetime_from_str.minute == now_datetime.minute
    assert datetime_from_str.second == now_datetime.second


def test_validate_datetime_valid_datetime():
    """Tests the validation of a future datetime

    :return:
    """

    assert validate_datetime(datetime.now(UTC).isoformat())


def test_validate_datetime_invalid_datetime():
    """Tests attempting to validate an invalid datetime

    :return:
    """

    with pytest.raises(InvalidDatetimeFormatError):
        validate_datetime("This is totally a valid datetime")


def test_validate_future_datetime_valid_future_datetime():
    """Tests the validation of a future datetime

    :return:
    """

    assert validate_future_datetime(datetime.now(UTC) + timedelta(hours=1))


def test_validate_future_datetime_past_datetime():
    """Tests the validation of a future datetime

    :return:
    """

    assert not validate_future_datetime(datetime.now(UTC) + timedelta(hours=-1))


def test_validate_future_datetime_from_string_valid_future_datetime():
    """Tests the validation of a future datetime

    :return:
    """

    assert validate_future_datetime_from_string((datetime.now(UTC) + timedelta(hours=1)).isoformat())


def test_validate_future_datetime_from_string_past_datetime():
    """Tests the validation of a future datetime

    :return:
    """

    assert not validate_future_datetime_from_string((datetime.now(UTC) + timedelta(hours=-1)).isoformat())


def test_create_user_jwt_expire_date_valid():
    """Tests the validation of the jwt expiry date

    :return:
    """

    datetime_now = datetime.now(UTC)
    jwt_expiry_date = datetime.fromisoformat(create_user_jwt_expiry_date())

    expected_expiry_date = datetime_now + timedelta(minutes=__JWT_TIMEOUT)

    assert jwt_expiry_date.year == expected_expiry_date.year
    assert jwt_expiry_date.month == expected_expiry_date.month
    assert jwt_expiry_date.day == expected_expiry_date.day
    assert jwt_expiry_date.hour == expected_expiry_date.hour
    assert jwt_expiry_date.minute == expected_expiry_date.minute
    assert jwt_expiry_date.second == expected_expiry_date.second
