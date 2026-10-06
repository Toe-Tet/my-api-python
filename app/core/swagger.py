from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from app.router import v1_router, v2_router


def build_versioned_openapi(version_name: str, routes: list):
    schema = get_openapi(
        title=f"KonektAgri API {version_name}",
        version=version_name,
        routes=routes,
    )
    schema["paths"] = {
        f"/api{path}": definition
        for path, definition in schema.get("paths", {}).items()
    }
    return schema


def setup_swagger(app: FastAPI):
    @app.get("/openapi/v1.json", include_in_schema=False)
    async def openapi_v1():
        return build_versioned_openapi("v1", v1_router.routes)

    @app.get("/openapi/v2.json", include_in_schema=False)
    async def openapi_v2():
        return build_versioned_openapi("v2", v2_router.routes)

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        response = get_swagger_ui_html(
            openapi_url="/openapi/v1.json",
            title="KonektAgri API Docs",
            swagger_ui_parameters={
                "layout": "StandaloneLayout",
                "urls": [
                    {"url": "/openapi/v1.json", "name": "API v1"},
                    {"url": "/openapi/v2.json", "name": "API v2"},
                ],
                "urls.primaryName": "API v1",
            },
        )
        html = response.body.decode("utf-8")
        html = html.replace(
            '<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>\n'
            '    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>',
            1,
        )
        html = html.replace(
            "SwaggerUIBundle.SwaggerUIStandalonePreset",
            "SwaggerUIStandalonePreset",
            1,
        )
        html = html.replace("        url: '/openapi/v1.json',\n", "", 1)
        return HTMLResponse(content=html, status_code=response.status_code)
