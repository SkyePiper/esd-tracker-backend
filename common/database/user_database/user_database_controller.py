"""Controller for the Users database

Controllers are the middle man between and endpoint and the database. They perform as much of the validation as
possible.

Controllers cannot be imported by other controllers - This is likely to cause a circular import if allowed. Controllers
can only import adapters.
"""

from common.auth.password_utils import hash_password
from common.database.base_database.database_controller import \
    DatabaseController
from common.database.user_database.user_database_adaptor import \
    UserDatabaseAdaptor
from common.database.user_database.user_models import (UserModel,
                                                       UserUpdateModel)
from common.enums.permissions import Permissions


class UserController(DatabaseController):
    """Controller for the Users database"""

    def __init__(self):
        self.__user_adapter = UserDatabaseAdaptor()

    async def get_all_records(self, user: UserModel) -> list[UserModel]:
        """Gets all the records from the database

        :param user: The user making the request
        :return: The users
        """

        await self.check_permissions(user.permissions, [Permissions.GET_USER])
        return await self.__user_adapter.get_all_records()

    async def get_record_by_id(self, user: UserModel, record_id: int) -> UserModel:
        """Gets a record by its ID

        :param user: The user making the request
        :param record_id: The ID of the record to get
        :return: The record
        """
        await self.check_permissions(user.permissions, [Permissions.GET_USER])

        return await self.__user_adapter.get_record_by_id(record_id)

    async def add_record(self, user: UserModel, new_record: UserModel) -> UserModel:
        """Adds a record to the database

        :param user: The user attempting to add the record
        :param new_record: The new record
        :return:
        """

        await self.check_permissions(user.permissions, [Permissions.CREATE_USER])

        new_record.password = await hash_password(new_record.password)

        return await self.__user_adapter.add_record(new_record)

    async def update_record(self, user: UserModel, record_id: int, record_updates: UserUpdateModel) -> UserModel:
        """Updates a record

        :param user: The user attempting to update the record
        :param record_id: The ID of the record to update
        :param record_updates: The updates to the record
        :return: The updated record
        """

        if record_id == user.id:
            await self.check_permissions(user.permissions, [Permissions.UPDATE_SELF])

            # The user cannot update their own ESD training dates
            record_updates.last_training_date = None
            record_updates.next_training_date = None

        else:
            await self.check_permissions(user.permissions, [Permissions.UPDATE_OTHER_USERS])

        return await self.__user_adapter.update_record(record_id, record_updates)

    async def delete_record(self, user: UserModel, record_id: int):
        """Deletes a record from the database

        :param user: The user attempting to delete the record
        :param record_id: The ID of the record to delete
        :return:
        """

        await self.check_permissions(user.permissions, [Permissions.DELETE_USERS])

        return await self.__user_adapter.delete_record(record_id)
