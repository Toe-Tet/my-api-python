import structlog

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response import ErrorResponse


logger = structlog.get_logger()


def request_validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:

    errors = []

    sensitive_fields = {
        "password",
        "confirm_password",
    }

    for error in exception.errors():

        value = (
            "***" if error.get("loc")[-1] in sensitive_fields else error.get("input")
        )

        errors.append(
            {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": value,
            }
        )

    logger.warning(
        "validation.error",
        method=request.method,
        path=request.url.path,
        message="Validation error",
        status_code=422,
        errors=errors,
    )

    response = ErrorResponse(
        message="Validation error",
        errors=errors,
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(
            mode="json",
            exclude_none=True,
        ),
    )
