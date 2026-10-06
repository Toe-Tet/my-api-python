from datetime import datetime, timedelta, timezone
from app.core.config import settings

import jwt


class JwtService:
    def create_access_token(self, user_id: int) -> tuple[str, int]:
        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(seconds=settings.JWT_EXPIRES_IN)

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": expires_at,
        }

        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm="HS256",
        )

        return token, int(expires_at.timestamp())


jwt_service = JwtService()
