import logging
import re
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.exceptions.app_exception import AppException
from app.core.services.jwt_service import jwt_service
from app.core.tenancy import tenant_store, tenancy_manager
from fastapi_tenancy.core.exceptions import TenantNotFoundError
from fastapi_tenancy.utils.validation import validate_tenant_identifier
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
http_bearer = HTTPBearer(auto_error=False)


class TenantService:
    TENANT_IDENTIFIER_PATTERN = re.compile(r"[^a-z0-9]+")

    def build_tenant_identifier(self, tenant_name: str) -> str:
        identifier = self.TENANT_IDENTIFIER_PATTERN.sub(
            "-",
            tenant_name.strip().lower(),
        )
        identifier = re.sub(r"-+", "-", identifier).strip("-")

        if not identifier:
            raise AppException(
                message="Tenant name must contain letters or numbers",
                status_code=422,
            )

        if not identifier[0].isalpha():
            identifier = f"tenant-{identifier}"

        identifier = identifier[:63].rstrip("-")

        if len(identifier) < 3 or not validate_tenant_identifier(identifier):
            raise AppException(
                message=(
                    "Tenant name must produce a valid identifier with 3-63 lowercase "
                    "letters, numbers, or hyphens"
                ),
                status_code=422,
            )

        return identifier

    async def cleanup_registered_tenant(self, tenant_id: str) -> None:
        try:
            await tenancy_manager.delete_tenant(tenant_id, destroy_data=True)
        except Exception:
            logger.exception(
                "Failed to clean up tenant '%s' after registration error",
                tenant_id,
            )

    async def rollback_failed_registration(
        self,
        session: AsyncSession,
        tenant_id: str | None,
    ) -> None:
        await session.rollback()

        if tenant_id is not None:
            await self.cleanup_registered_tenant(tenant_id)


async def get_current_tenant_from_jwt(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer),
    ],
):
    if credentials is None:
        raise AppException(
            message="Authentication required",
            status_code=401,
        )

    payload = jwt_service.decode_access_token(credentials.credentials)
    tenant_id = payload.get("tenant_id")

    if not isinstance(tenant_id, str) or not tenant_id:
        raise AppException(
            message="Invalid access token",
            status_code=401,
        )

    try:
        return await tenant_store.get_by_id(tenant_id)
    except TenantNotFoundError as exc:
        raise AppException(
            message="Tenant not found",
            status_code=401,
        ) from exc


async def get_tenant_db_from_jwt(
    tenant: Annotated[object, Depends(get_current_tenant_from_jwt)],
) -> AsyncIterator[AsyncSession]:
    async with tenancy_manager.isolation_provider.get_session(tenant) as session:
        yield session


tenant_service = TenantService()
