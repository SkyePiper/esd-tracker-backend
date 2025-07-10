"""Abstract controller for a database

Controllers are the middle man between and endpoint and the database. They perform as much of the validation as
possible.

Controllers cannot be imported by other controllers - This is likely to cause a circular import if allowed. Controllers
can only import adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from common.database.user_database.user_models import UserModel
from common.enums.permissions import Permissions
from common.helper_functions.errors import UnauthorisedError
from pydantic import BaseModel


class DatabaseController(ABC):
    """Abstract database controller"""

    __instance: DatabaseController | None = None

    @abstractmethod
    def __init__(self):
        """Initialises the class"""

    @abstractmethod
    async def get_all_records(self, user: UserModel) -> list[BaseModel]:
        """Gets all the records from the database

        :param user: The user making the request
        :return: The records
        """

    @abstractmethod
    async def get_record_by_id(self, user: UserModel, record_id: int) -> BaseModel:
        """Gets a record by its ID

        :param user: The user making the request
        :param record_id: The ID of the record to get
        :return: The record
        """

    @abstractmethod
    async def add_record(self, user: UserModel, new_record: BaseModel) -> BaseModel:
        """Adds a record to the database

        :param user: The user attempting to add the record
        :param new_record: The new record
        :return:
        """

    @abstractmethod
    async def update_record(self, user: UserModel, record_id: int, record_updates: BaseModel) -> BaseModel:
        """Updates a record

        :param user: The user attempting to update the record
        :param record_id: The ID of the record to update
        :param record_updates: The updates to the record
        :return: The updated record
        """

    @abstractmethod
    async def delete_record(self, user: UserModel, record_id: int):
        """Deletes a record from the database

        :param user: The user attempting to delete the record
        :param record_id: The ID of the record to delete
        :return:
        """

    @staticmethod
    async def check_permissions(user_permissions: int, valid_permissions: list[Permissions]):
        """Checks a users permissions

        :param user_permissions: The permissions of the user
        :param valid_permissions: The valid permissions
        :return:
        :raises UnauthorisedError: If the user does not have any of the required permissions
        """
        valid_permissions.append(Permissions.ADMINISTER)
        for permission in valid_permissions:
            if user_permissions & permission:
                break
        else:
            raise UnauthorisedError()

    def __new__(cls, *args, **kwargs):
        """Creates a new instance of this connector if an instance doesn't already exist

        This overrides the default behaviour of the __new__() method, allowing for a singleton pattern.
        If this is the first time instantiating this specific type of connector, it will create a new instance of this
        class. However, if another instance of this class is attempted to be made, instead of creating a new object,
        it will use the same object as the first instantiation.
        Despite this being in the base class, this will allow each inherited class to be instantiated once with no
        conflicts between them.

        :param args:
        :param kwargs:
        """

        if not cls.__instance:
            print(f"Instantiating a new {cls.__name__}")
            cls.__instance = super().__new__(cls)

        return cls.__instance
