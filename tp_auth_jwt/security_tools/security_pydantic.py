import pathlib
from typing import Annotated, Any, Optional

from pydantic import Field
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings


def options_decoder(v):
    if isinstance(v, str):
        return v.split(",")
    return v


OptionsType = Annotated[Any, BeforeValidator(options_decoder)]


class _Databases(BaseSettings):
    REDIS_URI: str
    REDIS_TYPE: str = Field(default="default")
    REDIS_MASTER_SERVICE: str = Field(default="my_master")


class _Secrets(BaseSettings):
    LOCK_OUT_TIME_MINS: int = 30
    LEEWAY_IN_MINS: int = 10
    UNIQUE_KEY: str = "45c37939-0f75"
    TOKEN: str = "8674cd1d-2578-4a62-8ab7-d3ee5f9a"
    ISSUER: str = "prismaticain"
    ALG: str = "RS256"
    CUSTOM_SERVICE_KEY: str = "PRISMATICA#ALWAYS#AHEAD"


class _Services(BaseSettings):
    # Cors
    ENABLE_CORS: bool = True
    CORS_URLS: OptionsType = ["*.prismatica.in"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: OptionsType = ["GET", "POST", "DELETE", "PUT"]
    CORS_ALLOW_HEADERS: OptionsType = ["*"]

    # Security
    SECURE_ACCESS: bool = Field(default=False)
    SECURE_COOKIE: bool = Field(default=False)

    # Docs URL override
    SW_DOCS_URL: Optional[str] = None
    SW_REDOC_URL: Optional[str] = None
    SW_OPENAPI_URL: Optional[str] = None


class _BasePathConf(BaseSettings):
    BASE_PATH: str = "/code/data"


class _PathConf(BaseSettings):
    BASE_PATH: pathlib.Path = pathlib.Path(_BasePathConf().BASE_PATH)
    KEY_PATH: pathlib.Path = BASE_PATH / "keys"


class _DatabaseConstants(BaseSettings):
    REDIS_LOGIN_DB: int = Field(default=9)


Databases = _Databases()
Services = _Services()
Secrets = _Secrets()
PathConf = _PathConf()
DatabaseConstants = _DatabaseConstants()

__all__ = ["DatabaseConstants", "Services", "Databases", "PathConf", "Secrets"]
