"""Error regarding the database"""

from fastapi import HTTPException
from starlette import status


class RecordDoesNotExistError(HTTPException):
    """Error for when a fetched record does not exist in the database"""

    def __init__(self, message: str):
        """Instantiates the class

        :param message: The error message
        """

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class RecordStillExistsError(HTTPException):
    """Error for when a record was unable to be deleted"""

    def __init__(self, message: str):
        """Initialises the class

        :param message: The error message
        """

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
