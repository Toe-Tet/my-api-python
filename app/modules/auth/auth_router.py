from typing import Annotated

from fastapi import APIRouter, Depends
from app.core.response import (
    SuccessResponse,
    default_error_responses,
    response,
)
from app.data.db.session import get_session
from app.modules.auth.dtos import (
    LoginUserPayload,
    LoginUserResult,
    RegisterUserPayload,
    RegisterUserResult,
)
from app.modules.auth.auth_service import auth_service
from sqlmodel.ext.asyncio.session import AsyncSession

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register",
    response_model=SuccessResponse[RegisterUserResult],
    responses=default_error_responses(),
)
async def register_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    register_user_payload: RegisterUserPayload,
):
    user = await auth_service.register_user(session, register_user_payload)
    return response(
        data=RegisterUserResult.model_validate(user),
    )


@auth_router.post(
    "/login",
    response_model=SuccessResponse[LoginUserResult],
    responses=default_error_responses(),
)
async def login_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    login_user_payload: LoginUserPayload,
):
    login_result = await auth_service.login_user(session, login_user_payload)
    return response(
        data=LoginUserResult.model_validate(login_result),
    )
