# TP Auth 🔐

TP Auth is a comprehensive authentication and authorization solution designed specifically for TechPrismatica projects. It leverages FastAPI and Pydantic to provide a secure, scalable, and easy-to-integrate authentication system. With support for JWT-based access tokens, environment variable configurations for seamless deployment, and extensive customization options, TP Auth aims to streamline the security aspects of your applications.

This documentation covers everything from setting up environment variables, installing the package, to integrating TP Auth into your authorization and resource servers. Whether you're looking to secure your APIs, implement role-based access control (RBAC), or manage user authentication flows, TP Auth provides the tools and guidance necessary to achieve a robust security posture.

## Features ✨

- **JWT-Based Authentication**: Utilize JSON Web Tokens (JWT) for secure, stateless authentication across your services.
- **Environment Variable Configurations**: Easily configure your application's security settings through environment variables, making it adaptable to different deployment environments.
- **FastAPI Integration**: Seamlessly integrate with FastAPI applications, allowing for straightforward implementation of authentication and authorization mechanisms.
- **Role-Based Access Control (RBAC)**: Implement fine-grained access control to manage user permissions and secure your endpoints.
- **Customizable Authentication Flows**: Define custom methods for token creation, refresh, and user authentication to fit your application's specific needs.

## Getting Started 🚀

To get started with TP Auth, follow the sections below on installation, setting up environment variables, and integrating TP Auth into your FastAPI applications. Detailed examples and configurations are provided to ensure a smooth setup process.

For a complete guide on how to use TP Auth in your projects, refer to the [Table of Contents 📑](#table-of-contents-).

We hope TP Auth enhances the security of your TechPrismatica projects with its robust set of features and ease of use. Happy coding!

## Table of Contents 📑

- [TP Auth 🔐](#tp-auth-)
  - [Features ✨](#features-)
  - [Getting Started 🚀](#getting-started-)
  - [Table of Contents 📑](#table-of-contents-)
  - [Environment Variable Configurations 🛠️](#environment-variable-configurations-️)
  - [Installation 💾](#installation-)
  - [Usage 📋](#usage-)
    - [Using in Authorization Servers](#using-in-authorization-servers)
      - [Setting ENV Configuration for Authorization Server](#setting-env-configuration-for-authorization-server)
      - [Defining Access Token Creation Method](#defining-access-token-creation-method)
      - [Defining Access Token Refresh Method](#defining-access-token-refresh-method)
      - [Registering defined methods with fastapi generator](#registering-defined-methods-with-fastapi-generator)
    - [Using in Resource Servers](#using-in-resource-servers)
      - [Setting ENV Configuration for Resource Server](#setting-env-configuration-for-resource-server)
      - [Getting User Details](#getting-user-details)
      - [Adding RBAC to Route](#adding-rbac-to-route)
      - [Communication to other resource servers](#communication-to-other-resource-servers)
  - [Authors 👩‍💻👨‍💻](#authors-)

## Environment Variable Configurations 🛠️

|SNo.|Variable Name|Required|Default|
|---|-------------|--------|-------|
|1|DOCS_URL|❌|/docs|
|2|REDOC_URL|❌|/redoc|
|3|OPENAPI_URL|❌|/openapi.json|
|4|PUBLIC_KEY|❌|None|
|5|PRIVATE_KEY|❌|None|
|6|SECRET_KEY|❌|None|
|7|ALGORITHM|❌|HS256|
|8|ISSUER|❌|prismaticain|
|9|LEEWAY|❌|10|
|10|EXPIRY|❌|1440|
|11|AUTHORIZATION_SERVER|❌|False|
|12|AUTH_SCOPES|❌|None|
|13|TOKEN_URL|❌|/token|
|14|CORS_URLS|❌|["*.prismatica.in"]|
|15|CORS_ALLOW_CREDENTIALS|✅|True|
|16|CORS_ALLOW_METHODS|❌|["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"]|
|17|CORS_ALLOW_HEADERS|❌|["*"]|
|18|ENABLE_CORS|❌|True|

Note: For `CORS_URLS`, `CORS_ALLOW_METHODS`, and `CORS_ALLOW_HEADERS`, the default values are lists. Ensure to format them appropriately in your environment configuration.

## Installation 💾

```bash
pip install tp-auth
```

Note: tp-auth is only available through PyPi server of TechPrismatica, Please contact Organisation maintainers/Devops team for PyPi server creds and URL.

## Usage 📋

### Using in Authorization Servers

TP-Auth can be used to create the authorization server.

#### Setting ENV Configuration for Authorization Server

```env
# Let's Utility know this microservice is a authorization server.
AUTHORIZATION_SERVER = True

# Domain or Company Name.
ISSUER = prismaticain

# Acceptable time gap between client & server in mins.
LEEWAY = 10

# Expiry time for access token in mins.
EXPIRY = 1440

# Available authorization scopes in application. If not provided ingores scope checks.
AUTH_SCOPES = {"read": "Read Access", "write": "Write Access"}

# Cors configurations.
CORS_URLS = ["*.prismatica.in"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"]
CORS_ALLOW_HEADERS = ["*"]
ENABLE_CORS = True

# If Algorithm is set to HS256.
SECRET_KEY = SomeSecret

# If Algorithm is set to RS256.
PUBLIC_KEY = Base64 Encoded public key
PRIVATE_KEY = Base64 Encoded private key
```

#### Defining Access Token Creation Method

To facilitate secure and efficient access token creation, our method meticulously requires the specification of three critical parameters: **OAuth2PasswordRequestForm**, **Request**, and **Response**. These parameters are essential for accurately processing authentication requests, ensuring the integrity of the authentication flow, and providing a seamless user experience.
It should return a Token object.

Example:

```python
from fastapi import Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from tp_auth import JWTUtil, Token

def token_creator(creds: OAuth2PasswordRequestForm, request: Request, response: Response) -> Token:
    jwt_util = JWTUtil()
    payload = {
        "user_id": "user_099",
        "scopes": ["user:read", "user:write"],
        "username": "Admin",
        "issued_to": request.client.host,
    }
    access_token = jwt_util.encode(payload, 1)
    refresh_jwt_util = JWTUtil(token_type="refresh")
    refresh_token_payload = {
        "user_id": "user_099",
        "issued_to": request.client.host,
    }
    refresh_token = refresh_jwt_util.encode(refresh_token_payload, 5)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=5,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=1,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
```

#### Defining Access Token Refresh Method

The access token refresh method is designed with precision to ensure a secure and efficient token management process. It necessitates the definition of three pivotal parameters: **refresh_token**, **Request**, and **Response**. By accurately processing these parameters, the method guarantees the renewal of access tokens in a secure manner, ultimately returning a **Token** object to maintain a seamless and secure user session.

```python
from fastapi import HTTPException, Request, Response, status
from tp_auth import JWTUtil, Token

def refresh_access_token(refresh_token: str, request: Request, response: Response) -> Token:
    jwt_util = JWTUtil()
    token_details = jwt_util.decode(refresh_token)
    if request.client.host != token_details["issued_to"] or token_details["token_type"] != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    payload = {
        "user_id": "user_099",
        "scopes": ["user:read", "user:write"],
        "username": "Admin",
        "issued_to": request.client.host,
    }
    access_token = jwt_util.encode(payload, 1)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=1,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
```

#### Registering defined methods with fastapi generator

```python
from fastapi import APIRouter
from tp_auth import FastAPIConfig, generate_fastapi_app

test_route = APIRouter()

app_config = FastAPIConfig(
    title="Test API",
    version="0.1.0",
    description="Test API for TP Auth",
    root_path="",
)

app = generate_fastapi_app(
    app_config=app_config,
    routers=[test_route],
    token_route_handler=token_creator,
    refresh_route_handler=refresh_access_token,
)
```

### Using in Resource Servers

TP Auth can be used in resource servers to authenticate user and provide resources.

#### Setting ENV Configuration for Resource Server

```env
# Available authorization scopes in application. If not provided ingores scope checks.
AUTH_SCOPES = {"read": "Read Access", "write": "Write Access"}

# If Algorithm is set to HS256.
SECRET_KEY = SomeSecret

# If Algorithm is set to RS256.
PUBLIC_KEY = Base64 Encoded public key
```

#### Getting User Details

```python
from tp_auth import UserInfo

@test_route.get("/user")
def get_user(user: UserInfo):
    return f"Hello {user.username}"
```

#### Adding RBAC to Route

```python
from fastapi import Security
from tp_auth import AuthValidatorInstance, UserInfoSchema

@test_route.get("/user")
def get_user(user: Annotated[UserInfoSchema, Security(AuthValidatorInstance, scopes=["user:write"])]):
    return f"Hello {user.username}"
```

#### Communication to other resource servers

```python
from tp_auth import TPRequestorInstance

@test_route.get("/forwarded")
def get_forwarded(requestor: TPRequestorInstance):
    resp = requestor.get(url="http://localhost:8001/user")
    return resp.text
```

## Authors 👩‍💻👨‍💻

- [<img src="https://avatars.githubusercontent.com/faizanazim11" width="40" height="40" style="border-radius:50%; vertical-align: middle;" alt="GitHub"/>](https://github.com/faizanazim11) [Faizan Azim](mailto:faizanazim11@gmail.com) - [<img src="https://github.githubassets.com/images/icons/emoji/octocat.png" width="40" height="40" style="vertical-align: middle;" alt="GitHub"/>](https://github.com/faizanazim11)
