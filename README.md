# TP Auth JWT

## Table of Contents

- [TP Auth JWT](#tp-auth-jwt)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Environment Variables](#environment-variables)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Getting FastAPI security configured app](#getting-fastapi-security-configured-app)
    - [Getting meta information in services](#getting-meta-information-in-services)
    - [Communicating with other UT services](#communicating-with-other-ut-services)
  - [Authors](#authors)

## Introduction

Security Package for TechPrismatica modules.

## Environment Variables

| Sno | Env Name                  | Default                               |
| --- | ------------------------- | ------------------------------------- |
| 1   | MONGO\_URI                |                                       |
| 2   | REDIS\_URI                |                                       |
| 3   | REDIS\_LOGIN\_DB          | 9                                     |
| 6   | SIGNATURE\_KEY\_SIZE      | 1024                                  |
| 7   | BASE\_PATH                | /code/data                            |

## Installation

```bash
pip install tp-auth-jwt
```

## Usage

### Getting FastAPI security configured app

Using this method will take care of adding health check, security, cors to the app.

```python
# Import FastAPIConfig and generate_fastapi_app.
from tp_auth_jwt import FastAPIConfig, generate_fastapi_app

# Create an instance of FastAPIConfig by passing title, version, description and root_path, Optionally - tags_metadata.

fastapi_config = FastAPIConfig(
    title="Example",
    version="1.0.0",
    description="Example",
    root_path="/example",
    tags_metadata=[
        {
            "name": "Example",
            "description": "Example",
        }
    ]
)

# Generate FastAPI app by passing FastAPIConfig instance and routers list and project_name.
app = generate_fastapi_app(app_config=fastapi_config, routers=[api_router], project_name="example")
```

__Note:__ *The generated FastAPI app will not have default TechPrismatica docs enabled, for enabling it pass __*enable_default_openapi=True*__ to __*generate_fastapi_app*__ method.*

The default docs will add *"Operational Services"* tag_metadata to the app openapi docs, If you want to configure it manually, you can pass __*disable_operation_default=True__*to the *__generate_fastapi_app*** method.

### Getting meta information in services

```python
# Import AuthInfo.
from tp_auth_jwt import AuthInfo

# Add AuthInfo as a parameter to the service method.
@router.get("/example")
def test(meta: AuthInfo):
    print(meta.model_dump())
    return "Hello World"
```

### Communicating with other UT services

```python
# Import AuthRequest
from tp_auth_jwt import AuthRequest

# Create an instance of AuthRequest by passing the module proxy.
request = AuthRequest("http://www.example.com")

# Call the service method by passing the method path and required payload.
response = request.post("/example", json={"key": "value"})
```

__Note:__ *The required __login-token__ will be automatically added to the request __*header*__ and __*cookies*__.*

## Authors

- [Faizan Azim](mailto:faizanazim11@gmail.com)
