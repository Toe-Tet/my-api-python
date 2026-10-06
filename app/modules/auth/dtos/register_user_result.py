from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class RegisterUserResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
