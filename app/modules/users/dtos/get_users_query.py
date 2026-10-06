from pydantic import BaseModel, Field


class GetUsersQuery(BaseModel):
    page: int = Field(default=1, ge=1, example=1)
    size: int = Field(default=10, ge=1, le=100, example=10)
