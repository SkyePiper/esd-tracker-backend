"""Controller for the Training Sessions database

Controllers are the middle man between and endpoint and the database. They perform as much of the validation as
possible.

Controllers cannot be imported by other controllers - This is likely to cause a circular import if allowed. Controllers
can only import adapters.
"""

from common.database.base_database.database_controller import DatabaseController
from common.database.base_database.database_errors import RecordDoesNotExistError
from common.database.training_session_database.training_session_database_adaptor import TrainingSessionDatabaseAdaptor
from common.database.training_session_database.training_session_models import (
    TrainingSessionModel,
    TrainingSessionUpdateModel,
    TrainingSessionUserModel,
)
from common.database.user_database.user_database_adaptor import UserDatabaseAdaptor
from common.database.user_database.user_models import UserModel
from common.database.user_session_inter_database.user_session_inter_database_adaptor import (
    UserSessionInterDatabaseAdapter,
)
from common.database.user_session_inter_database.user_session_inter_models import (
    UserSessionInterModel,
    UserSessionInterUpdateModel,
)
from common.enums.permissions import Permissions
from common.enums.user_session_attendance import Attendance
from pydantic import BaseModel


class TrainingSessionController(DatabaseController):
    """Controller for the TrainingSessions database"""

    def __init__(self):
        self.__training_session_database_adapter = TrainingSessionDatabaseAdaptor()
        self.__user_session_inter_database_adapter = UserSessionInterDatabaseAdapter()
        self.__user_database_adapter = UserDatabaseAdaptor()

    async def get_all_records(self, user: UserModel) -> list[TrainingSessionModel]:
        """Gets all the records from the database

        :param user: The user making the request
        :return: The records
        """

        await self.check_permissions(user.permissions, [Permissions.GET_TRAINING_SESSION])
        return await self.__training_session_database_adapter.get_all_records()

    async def get_record_by_id(self, user: UserModel, record_id: int) -> TrainingSessionModel:
        """Gets a record by its ID

        :param user: The user making the request
        :param record_id: The ID of the record to get
        :return: The record
        """
        await self.check_permissions(user.permissions, [Permissions.GET_TRAINING_SESSION])

        return await self.__training_session_database_adapter.get_record_by_id(record_id)

    async def get_training_session_attendance(self, user: UserModel, session_id: int) -> list[TrainingSessionUserModel]:
        """Gets the training session attendance

        :param user: The user making the request
        :param session_id: The ID of the training session
        :return: The attendance record for the training session
        """

        await self.check_permissions(user.permissions, [Permissions.GET_TRAINING_SESSION])

        try:
            items = await self.__user_session_inter_database_adapter.get_all_records_with_session_id(session_id)
        except RecordDoesNotExistError:
            # If no records exist, we still want to send a success response to the database - it just means that
            # no users have any attendance records for this training session
            return []

        updated_models = []
        for item in items:
            user_data = await self.__user_database_adapter.get_record_by_id(item.user_id)
            updated_models.append(
                TrainingSessionUserModel(
                    training_session_id=item.training_session_id,
                    forename=user_data.forename,
                    surname=user_data.surname,
                    email=user_data.email,
                    attendance_type=item.user_attendance_type,
                )
            )

        return updated_models

    async def get_user_attendance(self, user: UserModel, user_id: int) -> list[UserSessionInterModel]:
        """Gets the attendance for a user

        :param user: The user making the request
        :param user_id: The ID of the user to get the attendance for
        :return: The attendance of the user
        """

        await self.check_permissions(user.permissions, [Permissions.GET_TRAINING_SESSION])

        return await self.__user_session_inter_database_adapter.get_all_records_with_user_id(user_id)

    async def mark_user_attendance(
        self, user: UserModel, session_id: int, user_email: str, attendance: Attendance
    ) -> UserSessionInterModel:
        """Marks the users attendance for a training session

        :param user: The user making the request
        :param session_id: The ID of the training session
        :param user_email: The email of the user
        :param attendance: The attendance type
        :return: The attendance record
        """

        await self.check_permissions(user.permissions, [Permissions.GET_TRAINING_SESSION])

        # Make sure the user and session exist
        user_to_update = await self.__user_database_adapter.get_record_by_email(user_email)
        await self.__training_session_database_adapter.get_record_by_id(session_id)

        keys = {"user_id": user_to_update.id, "training_session_id": session_id}
        # Check if there is a attendance record for the user already
        try:
            await self.__user_session_inter_database_adapter.get_record_by_ids(keys)

            # There is an existing record - update it with the new attendance
            return await self.__user_session_inter_database_adapter.update_ck_record(
                UserSessionInterUpdateModel(user_attendance_type=attendance), keys
            )
        except RecordDoesNotExistError:
            # There is no current record in the database - create one!
            return await self.__user_session_inter_database_adapter.add_ck_record(
                UserSessionInterModel(
                    user_id=user_to_update.id, training_session_id=session_id, user_attendance_type=attendance
                ),
                keys,
            )

    async def add_record(self, user: UserModel, new_record: TrainingSessionModel) -> TrainingSessionModel:
        """Adds a record to the database

        :param user: The user attempting to add the record
        :param new_record: The new record
        :return:
        """

        await self.check_permissions(user.permissions, [Permissions.CREATE_TRAINING_SESSION])

        return await self.__training_session_database_adapter.add_record(new_record)

    async def update_record(
        self, user: UserModel, record_id: int, record_updates: TrainingSessionUpdateModel
    ) -> TrainingSessionModel:
        """Updates a record

        :param user: The user attempting to update the record
        :param record_id: The ID of the record to update
        :param record_updates: The updates to the record
        :return: The updated record
        """

        await self.check_permissions(user.permissions, [Permissions.UPDATE_TRAINING_SESSIONS])

        return await self.__training_session_database_adapter.update_record(record_id, record_updates)

    async def delete_record(self, user: UserModel, record_id: int):
        """Deletes a record from the database

        :param user: The user attempting to delete the record
        :param record_id: The ID of the record to delete
        :return:
        """

        await self.check_permissions(user.permissions, [Permissions.DELETE_TRAINING_SESSIONS])

        return await self.__training_session_database_adapter.delete_record(record_id)
