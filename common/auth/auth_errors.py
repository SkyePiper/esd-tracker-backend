"""Errors relating to the auth"""

from fastapi import HTTPException
from starlette import status


class InvalidAuthError(HTTPException):
    """Error for when a fetched record does not exist in the database"""

    def __init__(self):
        """Instantiates the class"""

        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username or Password")


class AuthTimeoutError(HTTPException):
    """Error for when a users auth has timed out"""

    def __init__(self):
        """Instantiates the class"""

        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth has timed out")
