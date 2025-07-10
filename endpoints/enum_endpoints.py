"""Endpoints for getting data about enums"""

from common.enums.models import EnumItemModel, EnumModel, EnumResponseModel
from common.enums.permissions import Permissions
from common.enums.user_session_attendance import Attendance
from common.responses import DEFAULT_RESPONSES
from fastapi import APIRouter

router = APIRouter(
    prefix="/enums",
    tags=["Enums"],
    responses=DEFAULT_RESPONSES,
)


@router.get("/permissions", tags=["Get"], response_model=EnumResponseModel, summary="Gets all the valid Permissions")
async def get_permissions() -> EnumResponseModel:
    """Gets all the valid permissions

    :return: The valid permissions
    """

    values = [EnumItemModel(name=item.name.title().replace("_", " "), value=item.value) for item in Permissions]
    return EnumResponseModel(data=EnumModel(enum_name="Permissions", enum_items=values))


@router.get(
    "/user_session_attendance",
    tags=["Get"],
    response_model=EnumResponseModel,
    summary="Gets all the valid User Session Attendance items",
)
async def get_user_session_attendance() -> EnumResponseModel:
    """Gets all the valid permissions

    :return: The valid permissions
    """

    values = [EnumItemModel(name=item.name.title().replace("_", " "), value=item.value) for item in Attendance]
    return EnumResponseModel(data=EnumModel(enum_name="Attendance", enum_items=values))
