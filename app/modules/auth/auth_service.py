from app.core.exceptions.app_exception import AppException
from app.core.services.jwt_service import jwt_service
from app.core.services.tenant_service import tenant_service
from app.data.models.tenant import Tenant
from app.data.models.user import User
from app.modules.auth.dtos import LoginUserPayload, RegisterUserPayload
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

import logging

logger = logging.getLogger(__name__)

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(),))


class AuthService:
    async def register_user(
        self,
        session: AsyncSession,
        register_user_payload: RegisterUserPayload,
    ):
        """Register a new user."""
        normalized_tenant_name = register_user_payload.tenant_name.strip()
        tenant_database_name = tenant_service.build_tenant_database_name(
            normalized_tenant_name
        )

        result = await session.exec(
            select(User).where(User.email == register_user_payload.email)
        )
        existing_user = result.first()

        if existing_user:
            raise AppException(
                message="Email already exists",
                status_code=422,
            )

        tenant_result = await session.exec(
            select(Tenant).where(
                func.lower(Tenant.name) == normalized_tenant_name.lower()
            )
        )
        existing_tenant = tenant_result.first()

        if existing_tenant:
            raise AppException(
                message="Tenant name already exists",
                status_code=422,
            )

        if await tenant_service.tenant_database_exists(tenant_database_name):
            raise AppException(
                message="Tenant database already exists",
                status_code=422,
            )

        database_created = False

        try:
            await tenant_service.create_tenant_database(tenant_database_name)
            database_created = True
            await tenant_service.run_tenant_migrations(tenant_database_name)

            tenant = Tenant(name=normalized_tenant_name)
            session.add(tenant)
            await session.flush()

            user = User(
                username=register_user_payload.username,
                email=register_user_payload.email,
                phone=register_user_payload.phone,
                password=password_hash.hash(register_user_payload.password),
                tenant_id=tenant.id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        # except AppException:
        #     await session.rollback()

        #     if database_created:
        #         await _cleanup_tenant_database(tenant_database_name)

        #     raise
        # except SQLAlchemyError:
        #     await session.rollback()

        #     if database_created:
        #         await _cleanup_tenant_database(tenant_database_name)

        #     logger.exception(
        #         "Failed to register user for tenant '%s'", normalized_tenant_name
        #     )
        #     raise AppException(
        #         message="Unable to register user",
        #         status_code=500,
        #     )
        except Exception:
            await session.rollback()

            if database_created:
                await tenant_service.cleanup_tenant_database(tenant_database_name)

            logger.exception(
                "Failed to provision tenant database '%s'",
                tenant_database_name,
            )
            raise AppException(
                message="Unable to create tenant database",
                status_code=500,
            )

    async def login_user(
        self,
        session: AsyncSession,
        login_user_payload: LoginUserPayload,
    ):
        result = await session.exec(
            select(User).where(User.email == login_user_payload.email)
        )

        user = result.first()

        if user is None:
            raise AppException(
                message="Invalid email or password",
                status_code=401,
            )

        if not password_hash.verify(
            login_user_payload.password,
            user.password,
        ):
            raise AppException(
                message="Invalid email or password",
                status_code=401,
            )

        if not user.is_active:
            raise AppException(
                message="User account is inactive",
                status_code=403,
            )

        # Generate your JWT here
        token, expires_at = jwt_service.create_access_token(user.id)

        return {
            "token": token,
            "expires_at": expires_at,
            "user": user,
        }


auth_service = AuthService()
