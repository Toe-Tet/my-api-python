from app.data.models.user import User
from app.modules.users.dtos import GetUsersQuery
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

import logging

logger = logging.getLogger(__name__)


class UserService:
    async def get_users(
        self,
        session: AsyncSession,
        tenant_id: str,
        query: GetUsersQuery,
    ) -> tuple[list[User], int]:
        total_items_result = await session.exec(
            select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
        )
        total_items = total_items_result.one()

        offset = (query.page - 1) * query.size
        result = await session.exec(
            select(User)
            .where(User.tenant_id == tenant_id)
            .order_by(User.id)
            .offset(offset)
            .limit(query.size)
        )

        return list(result.all()), total_items


user_service = UserService()
