from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class GetUsersResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
