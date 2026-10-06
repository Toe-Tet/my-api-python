import logging
import re

from app.core.exceptions.app_exception import AppException
from app.core.tenancy import tenancy_manager
from fastapi_tenancy.core.exceptions import TenancyError
from fastapi_tenancy.migrations.manager import MigrationError
from fastapi_tenancy.utils.validation import validate_tenant_identifier
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)


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

    def build_register_exception(
        self,
        exception: Exception,
        tenant_identifier: str,
    ) -> AppException:
        if isinstance(exception, ValueError):
            return AppException(
                message=str(exception),
                status_code=422,
            )

        if isinstance(exception, (MigrationError, TenancyError)):
            logger.exception(
                "Failed to provision tenant '%s' through fastapi-tenancy",
                tenant_identifier,
            )
            return AppException(
                message="Unable to provision tenant",
                status_code=500,
            )

        logger.exception(
            "Failed to register tenant '%s'",
            tenant_identifier,
        )
        return AppException(
            message="Unable to register user",
            status_code=500,
        )


tenant_service = TenantService()
