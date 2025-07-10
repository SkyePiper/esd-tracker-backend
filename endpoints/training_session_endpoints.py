"""Endpoints for the training sessions"""

from common.auth.auth import VALIDATE_USER
from common.database.training_session_database.training_session_database_controller import \
    TrainingSessionController
from common.database.training_session_database.training_session_models import (
    TrainingSessionAttendanceResponseModel, TrainingSessionModel,
    TrainingSessionResponseModel, TrainingSessionsResponseModel,
    TrainingSessionUpdateModel, TrainingSessionUserAttendanceResponseModel)
from common.database.user_session_inter_database.user_session_inter_models import \
    UserSessionInterResponseModel
from common.enums.user_session_attendance import Attendance
from common.responses import DEFAULT_RESPONSES, SuccessResponseModel
from fastapi import APIRouter

router = APIRouter(
    prefix="/training_sessions",
    tags=["Training Sessions"],
    responses=DEFAULT_RESPONSES,
)
training_session_controller = TrainingSessionController()


@router.get(
    "/{session_id}", tags=["Get"], response_model=TrainingSessionResponseModel, summary="Gets a Training Session"
)
async def get_user_by_id(user: VALIDATE_USER, session_id: int) -> TrainingSessionResponseModel:
    """Gets a training session by their ID

    :param user: The user making the request
    :param session_id: The ID of the training session to get
    :return: The training session
    """

    data = await training_session_controller.get_record_by_id(user, session_id)
    return TrainingSessionResponseModel(data=data)


@router.get(
    "/attendance/session/{session_id}",
    tags=["Get"],
    response_model=TrainingSessionAttendanceResponseModel,
    summary="Gets the attendance for a training session",
)
async def get_attendance(user: VALIDATE_USER, session_id: int) -> TrainingSessionAttendanceResponseModel:
    """Gets the attendance for a training session

    :param user: The user making the request
    :param session_id: The ID of the training session to get the attendance for
    :return: The attendance record for the training session
    """

    data = await training_session_controller.get_training_session_attendance(user, session_id)
    return TrainingSessionAttendanceResponseModel(data=data)


@router.get(
    "/attendance/user/{user_id}",
    tags=["Get"],
    response_model=TrainingSessionUserAttendanceResponseModel,
    summary="Gets the attendance for all the training sessions the user has attendance marked for",
)
async def get_all_user_attendance(user: VALIDATE_USER, user_id: int) -> TrainingSessionUserAttendanceResponseModel:
    """Gets the attendance for all training sessions that the user has got attendance for

    :param user: The user making the request
    :param user_id: The user to get the data for
    :return: The attendance for the user
    """

    data = await training_session_controller.get_user_attendance(user, user_id)
    return TrainingSessionUserAttendanceResponseModel(data=data)


@router.post(
    "/attendance",
    tags=["Post"],
    response_model=UserSessionInterResponseModel,
    summary="Sets the users attendance to a training session",
)
async def set_user_attendance(
    user: VALIDATE_USER, session_id: int, user_email: str, attendance: Attendance
) -> UserSessionInterResponseModel:
    """Sets the users attendance to a training session

    :param user: The user making the request
    :param session_id: The session ID to mark the attendance for
    :param user_email: The user to mark the attendance for
    :param attendance: The attendance to mark with
    :return: The attendance record
    """

    data = await training_session_controller.mark_user_attendance(user, session_id, user_email, attendance)
    return UserSessionInterResponseModel(data=data)


@router.get("", tags=["Get"], response_model=TrainingSessionsResponseModel, summary="Get all training sessions")
async def get_all_sessions(user: VALIDATE_USER) -> TrainingSessionsResponseModel:
    """Gets all the training sessions

    :param user: The user making the request
    :return: The training sessions
    """

    data = await training_session_controller.get_all_records(user)
    return TrainingSessionsResponseModel(data=data)


@router.post("", tags=["Create"], response_model=TrainingSessionResponseModel, summary="Creates a new Training Session")
async def create_new_user(user: VALIDATE_USER, new_session: TrainingSessionModel) -> TrainingSessionResponseModel:
    """Creates a new training session. The training session ID will be overwritten with the next valid ID

    :param user: The training session making the request
    :param new_session: The training session to create
    :return: The created training session
    """

    data = await training_session_controller.add_record(user, new_session)
    return TrainingSessionResponseModel(data=data)


@router.patch(
    "/{session_id}", tags=["Update"], response_model=TrainingSessionResponseModel, summary="Updates a Training Session"
)
async def update_user_by_id(
    user: VALIDATE_USER, session_id: int, session_updates: TrainingSessionUpdateModel
) -> TrainingSessionResponseModel:
    """Updates a training session if their ID is valid

    :param user: The user making the request
    :param session_id: The ID of the training session to updates
    :param session_updates: The updates to the training session
    :return: The updated training session
    """

    data = await training_session_controller.update_record(user, session_id, session_updates)
    return TrainingSessionResponseModel(data=data)


@router.delete(
    "/{session_id}", tags=["Delete"], response_model=SuccessResponseModel, summary="Deletes a Training Session"
)
async def delete_user_by_id(user: VALIDATE_USER, session_id: int) -> SuccessResponseModel:
    """Deletes a training session by their ID

    :param user: The user making the request
    :param session_id: The ID of the training session to delete
    :return:
    """

    await training_session_controller.delete_record(user, session_id)
    return SuccessResponseModel()
