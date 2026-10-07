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
INVALID_LOGIN_MESSAGE = "Invalid tenant, email, or password"


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
        except Exception:
            await tenant_service.rollback_failed_registration(session, tenant_id)

            raise

    async def login_user(
        self,
        session: AsyncSession,
        login_user_payload: LoginUserPayload,
    ):
        try:
            tenant = await tenant_store.get_by_identifier(
                login_user_payload.tenant_identifier
            )
        except TenantNotFoundError as exc:
            raise AppException(
                message="Tenant not found",
                status_code=401,
            ) from exc

        result = await session.exec(
            select(User).where(
                User.email == login_user_payload.email,
                User.tenant_id == tenant.id,
            )
        )

        user = result.first()

        if user is None:
            raise AppException(
                message=INVALID_LOGIN_MESSAGE,
                status_code=401,
            )

        if not password_hash.verify(
            login_user_payload.password,
            user.password,
        ):
            raise AppException(
                message=INVALID_LOGIN_MESSAGE,
                status_code=401,
            )

        if not user.is_active:
            raise AppException(
                message="User account is inactive",
                status_code=403,
            )

        token, expires_at = jwt_service.create_access_token(user.id, user.tenant_id)

        return {
            "token": token,
            "expires_at": expires_at,
            "user": {
                **user.model_dump(),
                "tenant": {
                    "id": tenant.id,
                    "name": tenant.name,
                    "identifier": tenant.identifier,
                },
            },
        }


auth_service = AuthService()
