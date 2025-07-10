"""Errors relating to the helper functions"""

from fastapi import HTTPException
from starlette import status


class InvalidDatetimeFormatError(HTTPException):
    """Error raised when an invalid datetime is passed"""

    def __init__(self, message: str):
        """Instantiates the class

        :param message: The error message
        """

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class UnauthorisedError(HTTPException):
    """Error for when a user attempts to do something they are not allowed to"""

    def __init__(self):
        """Instantiates the class"""

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You do not have the permissions to access that"
        )
