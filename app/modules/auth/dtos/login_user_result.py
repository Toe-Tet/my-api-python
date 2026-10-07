from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class LoginUserTenantResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    identifier: str


class LoginUserUserResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    phone: str
    is_active: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime | None
    tenant: LoginUserTenantResult


class LoginUserResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token: str
    expires_at: int
    user: LoginUserUserResult
