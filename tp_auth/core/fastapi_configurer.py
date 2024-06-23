from typing import Callable, Optional, Tuple

from fastapi import APIRouter, Cookie, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing_extensions import Annotated

from tp_auth.auth.auth_validator import AuthValidatorInstance
from tp_auth.auth.schemas import Token
from tp_auth.config import Service


class FastAPIConfig(BaseModel):
    title: str
    version: str
    description: str
    root_path: str
    docs_url: str = Service.docs_url
    redoc_url: str = Service.redoc_url
    openapi_url: str = Service.openapi_url
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
        openapi_schema["tags"] = app_config.tags_metadata
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi


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


def add_security(app: FastAPI, routers: list[APIRouter]) -> FastAPI:
    [app.include_router(router, dependencies=AuthValidatorInstance) for router in routers]
    return app


def add_cors(app: FastAPI) -> FastAPI:
    if Service.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=Service.cors_urls,
            allow_credentials=Service.cors_allow_credentials,
            allow_methods=Service.cors_allow_methods,
            allow_headers=Service.cors_allow_headers,
        )
    return app


def add_token_route(app: FastAPI, handler: Callable, asynced: bool = False) -> FastAPI:
    @app.post("/token", response_model=Token)
    async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
        if asynced:
            return await handler(form_data)
        return handler(form_data)

    return app


def add_refresh_route(app: FastAPI, handler: Callable, asynced: bool = False) -> FastAPI:
    @app.post("/refresh", response_model=Token)
    async def refresh(refresh_token: Annotated[str, Depends(Cookie())]) -> Token:
        if asynced:
            return await handler(refresh_token)
        return handler(refresh_token)

    return app


def generate_fastapi_app(
    app_config: FastAPIConfig,
    routers: list[APIRouter],
    project_name: str,
    disable_operation_default: bool = False,
    token_route_handler: Optional[Callable | Tuple[Callable, bool]] = None,
    refresh_route_handler: Optional[Callable | Tuple[Callable, bool]] = None,
) -> FastAPI:
    app = FastAPI(
        title=app_config.title,
        version=app_config.version,
        description=app_config.description,
        root_path=app_config.root_path,
        openapi_url=app_config.openapi_url,
        docs_url=app_config.docs_url,
        redoc_url=app_config.redoc,
    )
    app.openapi = get_custom_api(app, app_config, disable_operation_default)
    app = add_health_check(app, project_name)
    app = add_security(app, routers)
    app = add_cors(app)
    if token_route_handler:
        if isinstance(token_route_handler, tuple):
            app = add_token_route(app, token_route_handler[0], token_route_handler[1])
        else:
            app = add_token_route(app, token_route_handler)
    if refresh_route_handler:
        if isinstance(refresh_route_handler, tuple):
            app = add_refresh_route(app, refresh_route_handler[0], refresh_route_handler[1])
        else:
            app = add_refresh_route(app, refresh_route_handler)
    return app


__all__ = [
    "FastAPIConfig",
    "generate_fastapi_app",
]
