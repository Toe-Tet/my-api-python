from app.core.exceptions.app_exception import AppException
from app.core.tenancy import (
    tenant_migration_manager,
    tenant_store,
    tenancy_manager,
)
from app.core.services.jwt_service import jwt_service
from app.core.services.tenant_service import tenant_service
from app.data.models.user import User
from app.modules.auth.dtos import LoginUserPayload, RegisterUserPayload
from fastapi_tenancy.core.exceptions import TenantNotFoundError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
        tenant_identifier = tenant_service.build_tenant_identifier(
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

        try:
            await tenant_store.get_by_identifier(tenant_identifier)
            raise AppException(
                message="Tenant name already exists",
                status_code=422,
            )
        except TenantNotFoundError:
            pass

        tenant_id: str | None = None

        try:
            tenant = await tenancy_manager.register_tenant(
                identifier=tenant_identifier,
                name=normalized_tenant_name,
            )
            tenant_id = tenant.id
            await tenant_migration_manager.upgrade_tenant(tenant)

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
        except Exception as exception:
            await tenant_service.rollback_failed_registration(session, tenant_id)

            if isinstance(exception, AppException):
                raise

            raise tenant_service.build_register_exception(
                exception,
                tenant_identifier,
            ) from exception

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
