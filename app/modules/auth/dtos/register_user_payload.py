from pydantic import BaseModel, EmailStr, field_validator, Field


class RegisterUserPayload(BaseModel):
    tenant_name: str = Field(min_length=3, max_length=50, example="tenant1")
    username: str = Field(min_length=3, max_length=50, example="john_doe123")
    email: EmailStr = Field(min_length=3, max_length=50, example="john.doe@example.com")
    phone: str = Field(pattern=r"^\+[1-9]\d{7,14}$", example="+1234567890")
    password: str = Field(min_length=8, max_length=50, example="password")
    confirm_password: str = Field(min_length=8, max_length=50, example="password")

    @field_validator("confirm_password")
    @classmethod
    def check_passwords(cls, confirm_password, info):
        password = info.data.get("password")

        if password != confirm_password:
            raise ValueError("Passwords do not match")

        return confirm_password
