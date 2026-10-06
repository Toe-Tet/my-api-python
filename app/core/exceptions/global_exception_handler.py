import structlog
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response as FastAPIResponse
from sqlalchemy.exc import DatabaseError
from app.core.exceptions.app_exception import AppException

from app.core.response import ErrorResponse


logger = structlog.get_logger()


async def global_exception_middleware(
    request: Request,
    call_next: Callable[
        [Request],
        Awaitable[FastAPIResponse],
    ],
) -> FastAPIResponse:

    try:
        return await call_next(request)

    # ---------------------------------------------------------
    # Application / business exception
    # ---------------------------------------------------------
    except AppException as exception:

        logger.warning(
            "application.error",
            method=request.method,
            path=request.url.path,
            message=exception.message,
            data=exception.data,
            status_code=exception.status_code,
        )

        response = ErrorResponse(
            message=exception.message,
            data=exception.data,
        )

        return JSONResponse(
            status_code=exception.status_code,
            content=response.model_dump(mode="json", exclude_none=True),
        )

    # ---------------------------------------------------------
    # Database exception
    # ---------------------------------------------------------
    # except DatabaseError:

    #     logger.exception(
    #         "database.error",
    #         method=request.method,
    #         path=request.url.path,
    #         message="Database error",
    #         status_code=500,
    #     )

    #     response = ErrorResponse(
    #         message="Database error",
    #     )

    #     return JSONResponse(
    #         status_code=500,
    #         content=response.model_dump(mode="json", exclude_none=True),
    #     )

    # ---------------------------------------------------------
    # Unexpected exception
    # ---------------------------------------------------------
    except Exception as exception:

        logger.exception(
            "unexpected.error",
            method=request.method,
            path=request.url.path,
            message=str(exception),
            type=type(exception).__name__,
            status_code=500,
        )

        response = ErrorResponse(
            message="Internal server error",
        )

        return JSONResponse(
            status_code=500,
            content=response.model_dump(mode="json", exclude_none=True),
        )
