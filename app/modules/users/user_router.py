from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends
from app.core.response import (
    PaginatedResponse,
    PaginationMeta,
    default_error_responses,
    response,
)
from app.data.db.session import get_session
from app.modules.users.dtos import (
    GetUsersQuery,
    GetUsersResult,
)
from app.modules.users.user_service import user_service
from sqlmodel.ext.asyncio.session import AsyncSession


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get(
    "",
    response_model=PaginatedResponse[list[GetUsersResult]],
    responses=default_error_responses(),
)
async def get_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    query: Annotated[GetUsersQuery, Depends()],
):
    users, total_items = await user_service.get_users(session, query)
    total_pages = ceil(total_items / query.size) if total_items else 0

    return response(
        data=[GetUsersResult.model_validate(user) for user in users],
        meta=PaginationMeta(
            page=query.page,
            size=query.size,
            total_pages=total_pages,
            next_page=query.page + 1 if query.page < total_pages else None,
            previous_page=query.page - 1 if query.page > 1 else None,
            total_items=total_items,
        ),
    )
