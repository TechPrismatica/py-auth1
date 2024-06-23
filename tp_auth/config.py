from enum import StrEnum
from typing import Any, Optional

from fastapi.security import OAuth2PasswordBearer
from pydantic import BeforeValidator, Field, model_validator
from pydantic_settings import BaseSettings
from typing_extensions import Annotated


def options_decoder(v):
    if isinstance(v, str):
        return v.split(",")
    return v


OptionsType = Annotated[Any, BeforeValidator(options_decoder)]


class SupportedAlgorithms(StrEnum):
    HS256 = "HS256"
    RS256 = "RS256"


class _Service(BaseSettings):
    name: Optional[str] = Field("tp-auth-jwt", env="SERVICE_NAME")
    port: Optional[int] = Field(5678, env="PORT")
    host: Optional[str] = Field("0.0.0.0", env="HOST")
    docs_url: Optional[str] = Field("/docs", env="DOCS_URL")
    redoc_url: Optional[str] = Field("/redoc", env="REDOC_URL")
    openapi_url: Optional[str] = Field("/openapi.json", env="OPENAPI_URL")
    enable_cors: Optional[bool] = True
    cors_urls: OptionsType = ["*.prismatica.in"]
    cors_allow_credentials: bool = True
    cors_allow_methods: OptionsType = ["GET", "POST", "DELETE", "PUT"]
    cors_allow_headers: OptionsType = ["*"]


class _Secrets(BaseSettings):
    public_key: Optional[str] = Field(None, env="PUBLIC_KEY")
    private_key: Optional[str] = Field(None, env="PRIVATE_KEY")
    secret_key: Optional[str] = Field(None, env="SECRET_KEY")
    algorithm: SupportedAlgorithms = SupportedAlgorithms.HS256
    issuer: Optional[str] = Field("prismaticain", env="ISSUER")
    leeway: Optional[int] = Field(10, env="LEEWAY")
    expiry: Optional[int] = Field(1440, env="EXPIRY")
    authorization_server: Optional[bool] = Field(False, env="AUTHORIZATION_SERVER")
    scopes: Optional[dict] = Field(None, env="AUTH_SCOPES")
    token_url: Optional[str] = Field("/token", env="TOKEN_URL")

    @model_validator(mode="before")
    def check_secrets(cls, values) -> dict:
        if values["algorithm"] == SupportedAlgorithms.RS256:
            if not values["PUBLIC_KEY"]:
                raise ValueError("Public must be provided for RS256 algorithm")
            if values["AUTHORIZATION_SERVER"] and not values["PRIVATE_KEY"]:
                raise ValueError("Private key must be provided for RS256 algorithm when used as authorization server")
        elif values["algorithm"] == SupportedAlgorithms.HS256:
            if not values["secret_key"]:
                raise ValueError("Secret key must be provided for HS256 algorithm")
        return values


Secrets = _Secrets()
Service = _Service()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=Secrets.token_url, scopes=Secrets.scopes)

__all__ = ["Secrets", "SupportedAlgorithms"]
