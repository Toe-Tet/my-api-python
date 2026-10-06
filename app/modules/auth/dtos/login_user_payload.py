from pydantic import BaseModel, EmailStr, Field


class LoginUserPayload(BaseModel):
    email: EmailStr = Field(min_length=3, max_length=50, example="john.doe@example.com")
    password: str = Field(min_length=8, max_length=50, example="password")
