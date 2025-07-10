"""Endpoints for the user"""

from common.auth.auth import VALIDATE_USER
from common.database.user_database.user_database_controller import UserController
from common.database.user_database.user_models import (
    MinimisedUserDataModel,
    UserModel,
    UserResponseModel,
    UsersResponseModel,
    UserUpdateModel,
)
from common.responses import DEFAULT_RESPONSES, SuccessResponseModel
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["User"],
    responses=DEFAULT_RESPONSES,
)
user_controller = UserController()


@router.get("", tags=["Get"], response_model=UsersResponseModel, summary="Gets all the users")
async def get_all_users(user: VALIDATE_USER) -> UsersResponseModel:
    """Gets all the users

    :param user: The user making the request
    :return: The users
    """

    data = await user_controller.get_all_records(user)
    data = [MinimisedUserDataModel(**item.model_dump()) for item in data]
    return UsersResponseModel(data=data)


@router.get("/{user_id}", tags=["Get"], response_model=UserResponseModel, summary="Gets a user")
async def get_user_by_id(user: VALIDATE_USER, user_id: int) -> UserResponseModel:
    """Gets a user by their ID

    :param user: The user making the request
    :param user_id: The ID of the user to get
    :return: The user
    """

    data = await user_controller.get_record_by_id(user, user_id)
    return UserResponseModel(data=data)


@router.post("", tags=["Create"], response_model=UserResponseModel, summary="Creates a new user")
async def create_new_user(user: VALIDATE_USER, new_user: UserModel) -> UserResponseModel:
    """Creates a new user. The user ID will be overwritten with the next valid ID

    :param user: The user making the request
    :param new_user: The user to create
    :return: The created user
    """

    data = await user_controller.add_record(user, new_user)
    return UserResponseModel(data=data)


@router.patch("/{user_id}", tags=["Update"], response_model=UserResponseModel, summary="Updates a user")
async def update_user_by_id(user: VALIDATE_USER, user_id: int, user_updates: UserUpdateModel) -> UserResponseModel:
    """Updates a user if their ID is valid

    :param user: The user making the request
    :param user_id: The ID of the user to updates
    :param user_updates: The updates to the user
    :return: The updated user
    """

    data = await user_controller.update_record(user, user_id, user_updates)
    return UserResponseModel(data=data)


@router.delete("/{user_id}", tags=["Delete"], response_model=SuccessResponseModel, summary="Deletes a user")
async def delete_user_by_id(user: VALIDATE_USER, user_id: int) -> SuccessResponseModel:
    """Deletes a user by their ID

    :param user: The user making the request
    :param user_id: The ID of the user to delete
    :return:
    """

    await user_controller.delete_record(user, user_id)
    return SuccessResponseModel()
