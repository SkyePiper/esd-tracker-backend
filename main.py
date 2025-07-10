from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from uvicorn import run

from common.auth.auth import authenticate_user_by_email_password, create_user_jwt
from common.auth.auth_errors import AuthTimeoutError, InvalidAuthError
from common.auth.auth_models import JwtModel, UserJwtDataModel
from common.database.training_session_database.training_session_database_adaptor import TrainingSessionDatabaseAdaptor
from common.database.user_database.user_database_adaptor import UserDatabaseAdaptor
from common.database.user_session_inter_database.user_session_inter_database_adaptor import (
    UserSessionInterDatabaseAdapter,
)
from common.helper_functions.errors import UnauthorisedError
from common.responses import (
    AuthTimeoutResponseModel,
    BackendErrorResponseModel,
    InvalidAuthResponseModel,
    UnauthorisedResponseModel,
    ValidationErrorResponseModel,
)
from endpoints.enum_endpoints import router as enum_endpoints
from endpoints.training_session_endpoints import router as training_session_endpoints
from endpoints.user_endpoints import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events

    ## Instantiate the databases
    for database in [UserDatabaseAdaptor(), TrainingSessionDatabaseAdaptor(), UserSessionInterDatabaseAdapter()]:
        await database.load_db()

    yield  # This will stop here until it needs to do the shutdown events
    # Shutdown events


app = FastAPI(lifespan=lifespan)  #

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

app.include_router(user_router)
app.include_router(training_session_endpoints)
app.include_router(enum_endpoints)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    """Handles a validation error to make more sense to a user

    :param request: The incoming request
    :param error: The error raised
    :return: The response sent to the user
    """

    issues = []
    request_data = {}

    for item in error.args:
        for error in item:
            field = error["loc"][1]
            value = error["input"]

            if error["type"] == "value_error":
                issue_str = f"{field} - {str(error['ctx']['error'])}"

                issues.append(issue_str)
                request_data[field] = {"error": issue_str}

            else:
                field_given_type = repr(type(value)).replace("<class '", "").replace("'>", "")
                issue_str = f"{field} - Given {value} (Type {field_given_type}), expected type "

                field_expected_type = (
                    request.scope["route"].body_field.field_info.annotation.model_fields[field].annotation
                )
                field_expected_type = (
                    repr(field_expected_type).replace("|", "OR").replace("<class '", "").replace("'>", "")
                )
                issue_str += field_expected_type

                issues.append(issue_str)
                request_data[field] = {"expected": field_expected_type, "given": field_given_type, "value": value}

    validation_error = ValidationErrorResponseModel(
        message="Unable to process data; Invalid data given.",
        data=request_data,
    )

    return JSONResponse(
        status_code=validation_error.status,
        content=jsonable_encoder(validation_error, exclude={"status"}),
    )


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def handle_unauthorised_error(
    request: Request, error: InvalidAuthError | UnauthorisedError | AuthTimeoutError
) -> JSONResponse:
    """Handles an unauthorised error

    :param request: The incoming request
    :param error: The error raised
    :return: The response sent to the user
    """

    if isinstance(error, InvalidAuthError):
        response = InvalidAuthResponseModel()
    elif isinstance(error, UnauthorisedError):
        response = UnauthorisedResponseModel()
    elif isinstance(error, AuthTimeoutError):
        response = AuthTimeoutResponseModel()
    else:
        response = UnauthorisedResponseModel()

    return JSONResponse(status_code=response.status, content=jsonable_encoder(response, exclude={"status"}))


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> JwtModel:
    """Logs in the user, creating a JWT for them if successful

    :param form_data: The username and password for the user
    :return: The JWT for the user
    """

    user = await authenticate_user_by_email_password(form_data.username, form_data.password)
    token = await create_user_jwt(user)
    return token


if __name__ == "__main__":
    run(
        "main:app",
        use_colors=True,
    )
