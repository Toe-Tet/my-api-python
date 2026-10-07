from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_tenancy.middleware.tenancy import TenancyMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.tenancy import tenancy_manager
from app.core.exceptions.global_exception_handler import global_exception_middleware
from app.core.exceptions.http_exception_handler import http_exception_handler
from app.core.exceptions.request_validation_exception_handler import (
    request_validation_exception_handler,
)
from app.core.logger import setup_logging
from app.core.swagger import setup_swagger
from app.router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await tenancy_manager.close()


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

setup_logging()

app.exception_handler(RequestValidationError)(request_validation_exception_handler)
app.exception_handler(StarletteHTTPException)(http_exception_handler)

app.middleware("http")(global_exception_middleware)
app.add_middleware(
    TenancyMiddleware,
    manager=tenancy_manager,
    excluded_paths=[
        "/docs",
        "/openapi/v1.json",
        "/openapi/v2.json",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/tenancy",
        "/api/v2/auth/register",
        "/api/v2/auth/login",
        "/api/v2/tenancy",
    ],
)

setup_swagger(app)
app.include_router(router)
