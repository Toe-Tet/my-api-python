from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import structlog

from app.core.response import ErrorResponse

logger = structlog.get_logger()


def http_exception_handler(
    request: Request,
    exception: HTTPException,
) -> JSONResponse:

    message = str(exception.detail)

    logger.warning(
        "http.error",
        method=request.method,
        path=request.url.path,
        status_code=exception.status_code,
        message=message,
    )

    response = ErrorResponse(
        message=message,
    )

    return JSONResponse(
        status_code=exception.status_code,
        content=response.model_dump(mode="json", exclude_none=True),
    )
