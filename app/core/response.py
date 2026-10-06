from typing import Generic, TypeVar, Any

from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse


T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int | None = None
    size: int | None = None
    total_pages: int | None = None
    next_page: int | None = None
    previous_page: int | None = None
    total_items: int


class SuccessResponse(BaseModel, Generic[T]):
    message: str = "success"
    data: T | None = None


class PaginatedResponse(SuccessResponse[T], Generic[T]):
    meta: PaginationMeta | None = None


class ValidationErrorItem(BaseModel):
    type: str = Field(
        examples=["string_too_short"],
    )
    loc: list[str | int] = Field(
        examples=[["body", "password"]],
    )
    msg: str = Field(
        examples=["String should have at least 8 characters"],
    )
    input: Any | None = Field(
        default=None,
        examples=["***"],
    )


class ErrorResponse(BaseModel):
    message: str
    data: dict[str, Any] | None = None
    errors: list[ValidationErrorItem] | None = None


class Response(BaseModel, Generic[T]):
    message: str = "success"
    data: T | None = None
    meta: PaginationMeta | None = None
    errors: list[dict[str, Any]] | None = None


def default_error_responses() -> dict[int, dict[str, Any]]:
    return {
        422: {
            "model": ErrorResponse,
            "description": "Validation error or business error",
            "content": {
                "application/json": {
                    "examples": {
                        "validation_error": {
                            "summary": "Validation error",
                            "value": {
                                "message": "Validation error",
                                "errors": [
                                    {
                                        "type": "string_too_short",
                                        "loc": ["body", "password"],
                                        "msg": "String should have at least 8 characters",
                                        "input": "***",
                                    }
                                ],
                            },
                        },
                        "business_error": {
                            "summary": "Business error",
                            "value": {
                                "message": "Username, email, or phone number already exists",
                            },
                        },
                    }
                }
            },
        },
        500: {
            "model": ErrorResponse,
            "description": "Server error",
            "content": {
                "application/json": {
                    "examples": {
                        "database_error": {
                            "summary": "Database error",
                            "value": {
                                "message": "Database error",
                            },
                        },
                        "internal_server_error": {
                            "summary": "Internal server error",
                            "value": {
                                "message": "Internal server error",
                            },
                        },
                    }
                }
            },
        },
    }


def response(
    message: str = "success",
    data: T | None = None,
    meta: PaginationMeta | None = None,
) -> JSONResponse:
    body: SuccessResponse[T] | PaginatedResponse[T]

    if meta is None:
        body = SuccessResponse(
            message=message,
            data=data,
        )
    else:
        body = PaginatedResponse(
            message=message,
            data=data,
            meta=meta,
        )

    return JSONResponse(
        content=body.model_dump(mode="json", exclude_none=True),
    )
