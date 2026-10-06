from sqlalchemy.exc import DatabaseError
from app.core.exceptions.app_exception import AppException
from app.data.models.user import User
from app.modules.auth.dtos import LoginUserPayload, LoginUserResult, RegisterUserPayload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.services.jwt_service import create_access_token

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
        # Check if the username already exists
        result = await session.exec(
            select(User).where(User.email == register_user_payload.email)
        )

        existing_user = result.first()

        if existing_user:
            raise AppException(
                message="Email already exists",
                status_code=422,
            )

        user = User(
            username=register_user_payload.username,
            email=register_user_payload.email,
            phone=register_user_payload.phone,
            password=password_hash.hash(register_user_payload.password),
        )
        session.add(user)
        await session.commit()
        return user

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
        token, expires_at = create_access_token(user.id)

        return {
            "token": token,
            "expires_at": expires_at,
            "user": user,
        }


auth_service = AuthService()
