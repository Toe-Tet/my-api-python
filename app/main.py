from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions.global_exception_handler import global_exception_middleware
from app.core.exceptions.http_exception_handler import http_exception_handler
from app.core.exceptions.request_validation_exception_handler import (
    request_validation_exception_handler,
)
from app.core.logger import setup_logging
from app.core.swagger import setup_swagger
from app.router import router


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

setup_logging()

app.exception_handler(RequestValidationError)(request_validation_exception_handler)
app.exception_handler(StarletteHTTPException)(http_exception_handler)

app.middleware("http")(global_exception_middleware)

setup_swagger(app)
app.include_router(router)
