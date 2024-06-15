from tp_auth_jwt.security_tools.auth_util import (
    AuthenticationError,
    AuthRequest,
    ForbiddenError,
)
from tp_auth_jwt.security_tools.decorators import (
    AuthInfo,
    CookieAuthentication,
)
from tp_auth_jwt.security_tools.fastapi_config import (
    FastAPIConfig,
    generate_fastapi_app,
)
from tp_auth_jwt.security_tools.jwt_util import JWT
from tp_auth_jwt.security_tools.token_creation import create_token

"""
Usage Information:

FastAPI Generator:

Add the following code in the main.py file of the application:

from tp_auth_jwt import FastAPIConfig, generate_fastapi_app

app = generate_fastapi_app(
    app_config=FastAPIConfig(
        title="API",
        version="1.0.0",
        description="API",
        root_path="/api",
    ),
    routers=[api_router],
    project_name="example_project
)



Enabling Authentication:

Add the following code in the main.py file of the application:

from tp_auth_jwt import CookieAuthentication

if SECURE_ACCESS:
    auth = CookieAuthentication

app.include_router(router, dependencies=[Depends(auth)])

The above code will enable authentication for all the routes in the application.



Getting Cookies in services:

from tp_auth_jwt import AuthInfo

@router.get("/test")
def test(meta: AuthInfo):
    print(meta.model_dump())
    return "Hello World"



Communication with other TechPrismatica modules:

from tp_auth_jwt import AuthRequest

example_module_req = AuthRequest("http://www.example.com")

example_response = example_module_req.get("/test")


"""

__all__ = [
    "AuthInfo",
    "AuthRequest",
    "CookieAuthentication",
    "FastAPIConfig",
    "generate_fastapi_app",
    "JWT",
    "AuthenticationError",
    "ForbiddenError",
    "create_token",
]
