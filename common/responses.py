"""Common responses sent by the backend"""

from typing import Union

from pydantic import BaseModel, Field
from starlette import status


class BaseResponseModel(BaseModel):
    """Base response model for responses to the frontend"""

    status: int | None = Field(...)
    """The return code form the backend"""
    message: str | None = Field(...)
    """The message of the response"""
    data: BaseModel | dict | None = Field(None)
    """The data in the response"""


class BadRequestResponseModel(BaseResponseModel):
    """Model for when an error has been raised in the backend"""

    status: int = Field(status.HTTP_400_BAD_REQUEST, frozen=True)


class UnauthorisedResponseModel(BaseResponseModel):
    """Model for when the user attempts to access something they don't have access to"""

    status: int = Field(status.HTTP_401_UNAUTHORIZED, frozen=True)
    message: str = Field("You do not have the permissions to access that resource", frozen=True)


class InvalidAuthResponseModel(BaseResponseModel):
    """Model for when a user attempts to log in with an invalid auth"""

    status: int = Field(status.HTTP_401_UNAUTHORIZED, frozen=True)
    message: str = Field("Invalid username or password", frozen=True)


class AuthTimeoutResponseModel(BaseResponseModel):
    """Model for when a user attempts to log in with an invalid auth"""

    status: int = Field(status.HTTP_401_UNAUTHORIZED, frozen=True)
    message: str = Field("Authentication has timed out", frozen=True)


class UnknownResourceResponseModel(BaseResponseModel):
    """Model for when the user attempts to access something that doesn't exist"""

    status: int = Field(status.HTTP_404_NOT_FOUND, frozen=True)
    message: str = Field("That resource was not found", frozen=True)


class ValidationErrorResponseModel(BaseResponseModel):
    """Model for when there is a validation error"""

    status: int = Field(status.HTTP_422_UNPROCESSABLE_ENTITY, frozen=True)
    message: str = Field("Unable to process data; Invalid data given.")
    data: dict = Field()


class BackendErrorResponseModel(BaseResponseModel):
    """Model for when the backend fails"""

    status: int = Field(status.HTTP_500_INTERNAL_SERVER_ERROR, frozen=True)
    message: str = Field("Unhandled backend error")


class SuccessResponseModel(BaseResponseModel):
    """Model for a successful operation"""

    status: int = Field(status.HTTP_200_OK, frozen=True)
    message: str = Field("Success", frozen=True)


class CreatedResponseModel(BaseResponseModel):
    """Model for a successful creation operation"""

    status: int = Field(status.HTTP_201_CREATED, frozen=True)
    message: str = Field("Created", frozen=True)


DEFAULT_RESPONSES = {
    400: {"model": BadRequestResponseModel},
    401: {"model": Union[UnauthorisedResponseModel, AuthTimeoutResponseModel]},
    404: {"model": UnknownResourceResponseModel},
    422: {"model": ValidationErrorResponseModel},
    500: {"model": BackendErrorResponseModel},
}
