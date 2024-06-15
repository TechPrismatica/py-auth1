from typing import Callable, Optional

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from tp_auth_jwt.security_tools.decorators import CookieAuthentication
from tp_auth_jwt.security_tools.security_pydantic import Services


class FastAPIConfig(BaseModel):
    title: str
    version: str
    description: str
    root_path: str
    docs_url: str = Services.SW_DOCS_URL
    redoc_url: str = Services.SW_REDOC_URL
    openapi_url: str = Services.SW_OPENAPI_URL
    tags_metadata: Optional[list[dict]] = None
    exception_handlers: Optional[dict] = None


class StatusResponse(BaseModel):
    status: int = 200


def get_custom_api(app: FastAPI, app_config: FastAPIConfig, disable_operation_default: bool) -> Callable:
    if not disable_operation_default:
        app_config.tags_metadata = app_config.tags_metadata or []
        app_config.tags_metadata.append(
            {
                "name": "Operational Services",
                "description": "The **Operational Services** tag groups all the endpoints related to operational services provided by the TechPrismatica platform.",
            }
        )

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app_config.title,
            version=app_config.version,
            description=app_config.description,
            routes=app.routes,
            servers=app.servers,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": f"{app_config.root_path or ''}/static/ftdm_logo_{'dark' if Services.DOCS_DARK_LOGO else 'light'}.png",
            "altText": "FTDM Logo",
        }
        if openapi_schema.get("components", {}).get("securitySchemes", {}).get("CookieAuthentication", {}):
            openapi_schema["components"]["securitySchemes"]["CookieAuthentication"]["in"] = "header"
        openapi_schema["tags"] = app_config.tags_metadata
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi


def add_redoc(app: FastAPI, app_config: FastAPIConfig, redoc_url: str) -> FastAPI:
    def get_redoc_html(
        *,
        openapi_url: str,
        title: str,
        redoc_favicon_url: str = f"{app_config.root_path or ''}/static/ra_logo.png",
        with_google_fonts: bool = True,
    ) -> HTMLResponse:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>{title}</title>
        <!-- needed for adaptive design -->
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        """
        if with_google_fonts:
            html += """
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        """
        html += f"""
            <link rel="shortcut icon" href="{redoc_favicon_url}">
            <!--
            ReDoc doesn't change outer page styles
            -->
            <style>
            body {{
                margin: 0;
                padding: 0;
            }}
            </style>
            </head>
            <body>
                <div id="redoc-container"></div>
                <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
                <script src="https://cdn.jsdelivr.net/gh/wll8/redoc-try@1.4.9/dist/try.js"></script>
                <script>
                    initTry({{
                    openApi: `{openapi_url}`,
                    }})
                </script>
            </body>
            </html>
            """
        return HTMLResponse(html)

    @app.get(redoc_url, include_in_schema=False)
    async def get_redoc() -> HTMLResponse:
        title = app.title + " - Redoc"
        return get_redoc_html(openapi_url=f"{app_config.root_path or ''}{app.openapi_url}", title=title)

    return app


def add_docs(app: FastAPI, app_config: FastAPIConfig, docs_url: str) -> FastAPI:
    @app.get(docs_url, include_in_schema=False)
    async def get_docs() -> HTMLResponse:
        title = app.title + " - Swagger UI"
        return get_swagger_ui_html(
            openapi_url=f"{app_config.root_path or ''}{app.openapi_url}",
            title=title,
            swagger_favicon_url=f"{app_config.root_path or ''}/static/ra_logo.png",
            init_oauth=app.swagger_ui_init_oauth,
            swagger_ui_parameters=app.swagger_ui_parameters,
        )

    return app


def add_health_check(app: FastAPI, project_name: str) -> FastAPI:
    @app.get(
        f"/api/{project_name}/healthcheck",
        name="Health Check",
        tags=["Operational Services"],
        response_model=StatusResponse,
    )
    async def ping():
        """
        This function sends a ping request to the server and returns a StatusResponse object.
        """
        return StatusResponse()

    return app


def add_secure_cookie(app: FastAPI, routers: list[APIRouter]) -> FastAPI:
    auth = [Depends(CookieAuthentication)] if Services.SECURE_ACCESS else None
    [app.include_router(router, dependencies=auth) for router in routers]
    return app


def add_cors(app: FastAPI) -> FastAPI:
    if Services.ENABLE_CORS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=Services.CORS_URLS,
            allow_credentials=Services.CORS_ALLOW_CREDENTIALS,
            allow_methods=Services.CORS_ALLOW_METHODS,
            allow_headers=Services.CORS_ALLOW_HEADERS,
        )
    return app


def generate_fastapi_app(
    app_config: FastAPIConfig,
    routers: list[APIRouter],
    project_name: str,
    enable_default_openapi: bool = False,
    disable_operation_default: bool = False,
) -> FastAPI:
    redoc_url = app_config.redoc_url
    app_config.redoc_url = None
    docs_url = app_config.docs_url
    app_config.docs_url = None
    app = FastAPI(**app_config.model_dump(exclude={"tags_metadata"}), servers=None)
    app.mount("/static", StaticFiles(packages=["tp_auth_jwt"]), name="static")
    if redoc_url:
        app = add_redoc(app, app_config, redoc_url)
    if docs_url:
        app = add_docs(app, app_config, docs_url)
    app = add_health_check(app, project_name)
    app = add_secure_cookie(app, routers)
    app = add_cors(app)
    if enable_default_openapi:
        app.openapi = get_custom_api(app, app_config, disable_operation_default)
    return app


__all__ = ["generate_fastapi_app", "FastAPIConfig"]
