import asyncio
import re
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
import logging
from app.core.exceptions.app_exception import AppException

TENANT_NAME_PATTERN = re.compile(r"[^a-z0-9_]+")
VALID_DATABASE_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")

logger = logging.getLogger(__name__)


class TenantService:
    def build_tenant_database_name(self, tenant_name: str) -> str:
        normalized_name = tenant_name.strip().lower().replace(" ", "_")
        normalized_name = TENANT_NAME_PATTERN.sub("_", normalized_name)
        normalized_name = re.sub(r"_+", "_", normalized_name).strip("_")

        if not normalized_name:
            raise AppException(
                message="Tenant name must contain letters or numbers",
                status_code=422,
            )

        return f"{settings.TENANT_DATABASE_PREFIX}{normalized_name}"

    async def create_tenant_database(self, database_name: str) -> None:
        self._validate_database_name(database_name)

        engine = create_async_engine(
            settings.SQLALCHEMY_TENANT_DATABASE_URI,
            isolation_level="AUTOCOMMIT",
        )

        try:
            async with engine.connect() as connection:
                await connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        finally:
            await engine.dispose()

    async def tenant_database_exists(self, database_name: str) -> bool:
        self._validate_database_name(database_name)

        engine = create_async_engine(settings.SQLALCHEMY_TENANT_DATABASE_URI)

        try:
            async with engine.connect() as connection:
                result = await connection.execute(
                    text(
                        "SELECT 1 FROM pg_database WHERE datname = :database_name LIMIT 1"
                    ),
                    {"database_name": database_name},
                )
                return result.scalar() is not None
        finally:
            await engine.dispose()

    async def drop_tenant_database(self, database_name: str) -> None:
        self._validate_database_name(database_name)

        engine = create_async_engine(
            settings.SQLALCHEMY_TENANT_DATABASE_URI,
            isolation_level="AUTOCOMMIT",
        )

        try:
            async with engine.connect() as connection:
                await connection.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) "
                        "FROM pg_stat_activity "
                        "WHERE datname = :database_name "
                        "AND pid <> pg_backend_pid()"
                    ),
                    {"database_name": database_name},
                )
                await connection.execute(
                    text(f'DROP DATABASE IF EXISTS "{database_name}"')
                )
        finally:
            await engine.dispose()

    async def run_tenant_migrations(self, database_name: str) -> None:
        database_url = settings.build_database_uri(database_name)
        await asyncio.to_thread(self._run_tenant_migrations_sync, database_url)

    def _run_tenant_migrations_sync(self, database_url: str) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        config = Config(str(repo_root / "alembic_tenants.ini"))
        config.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(config, "head")

    def _validate_database_name(self, database_name: str) -> None:
        if not VALID_DATABASE_NAME_PATTERN.fullmatch(database_name):
            raise AppException(
                message="Generated tenant database name is invalid",
                status_code=422,
            )

    async def cleanup_tenant_database(self, database_name: str) -> None:
        try:
            await self.drop_tenant_database(database_name)
        except Exception:
            logger.exception(
                "Failed to clean up tenant database '%s'",
                database_name,
            )


tenant_service = TenantService()
