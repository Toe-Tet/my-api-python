from fastapi_tenancy.utils.validation import validate_tenant_identifier
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginUserPayload(BaseModel):
    tenant_identifier: str = Field(
        min_length=3,
        max_length=63,
        example="tenant-acme-farm",
    )
    email: EmailStr = Field(
        min_length=3,
        max_length=50,
        example="john.doe@example.com",
    )
    password: str = Field(min_length=8, max_length=50, example="password")

    @field_validator("tenant_identifier")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        normalized_value = value.strip().lower()

        if not validate_tenant_identifier(normalized_value):
            raise ValueError("tenant_identifier must be a valid tenant identifier")

        return normalized_value
