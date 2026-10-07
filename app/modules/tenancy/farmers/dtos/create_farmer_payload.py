from pydantic import BaseModel, Field


class CreateFarmerPayload(BaseModel):
    name: str = Field(min_length=3, max_length=100, example="John Doe")
    is_active: bool = Field(default=True, example=True)
