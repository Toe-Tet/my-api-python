from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class LoginUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class LoginUserResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token: str
    expires_at: int
    user: LoginUser
