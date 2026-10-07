from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.exceptions.app_exception import AppException


class JwtService:
    def create_access_token(self, user_id: int, tenant_id: str) -> tuple[str, int]:
        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(seconds=settings.JWT_EXPIRES_IN)

        payload = {
            "sub": str(user_id),
            "tenant_id": tenant_id,
            "iat": now,
            "exp": expires_at,
        }

        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm="HS256",
        )

        return token, int(expires_at.timestamp())

    def decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
            )
        except ExpiredSignatureError as exc:
            raise AppException(
                message="Access token has expired",
                status_code=401,
            ) from exc
        except InvalidTokenError as exc:
            raise AppException(
                message="Invalid access token",
                status_code=401,
            ) from exc

        return payload


jwt_service = JwtService()
