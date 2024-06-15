import json
import logging
from secrets import compare_digest
from typing import Annotated, Tuple

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security import APIKeyCookie
from fastapi.security.api_key import APIKeyBase
from pydantic import BaseModel, ConfigDict, Field
from starlette.datastructures import MutableHeaders

from tp_auth_jwt.exceptions import ErrorMessages
from tp_auth_jwt.security_tools.jwt_util import JWT
from tp_auth_jwt.security_tools.redis_conections import login_db
from tp_auth_jwt.security_tools.security_pydantic import Secrets, Services
from tp_auth_jwt.security_tools.token_creation import create_token


class _AuthInfo(BaseModel):
    user_id: str | None = ""
    ip_address: str | None = ""
    userId: str | None = ""
    login_token: str | None = Field(default="", validation_alias="login-token", serialization_alias="login-token")
    model_config = ConfigDict(populate_by_name=True)


class _CookieAuthentication(APIKeyBase):
    """
    Authentication backend using a cookie.
    Internally, uses a JWT token to store the data.
    """

    scheme: APIKeyCookie
    cookie_name: str
    cookie_secure: bool

    def __init__(
        self,
        cookie_name: str = "login-token",
    ):
        super().__init__()
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.scheme_name = "CookieAuthentication"
        self.cookie_name = cookie_name
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)
        self.login_redis = login_db
        self.jwt = JWT()

    def token_validation(self, token: str, login_token: str, host: str) -> Tuple[str, str, str]:
        decoded_token = self.jwt.validate(token=token)
        if not decoded_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        _token = decoded_token.get("token")
        _age = int(decoded_token.get("age", Secrets.LOCK_OUT_TIME_MINS))
        if any(
            [
                not compare_digest(Secrets.TOKEN, _token),
                login_token != decoded_token.get("uid"),
            ]
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            new_token = create_token(
                user_id=decoded_token.get("user_id"),
                ip=host,
                token=_token,
                age=_age,
                login_token=login_token,
            )
            return decoded_token.get("user_id"), new_token
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.args) from e

    async def update_headers_and_cookies(
        self, request: Request, response: Response, user_id: str, login_token: str
    ) -> None:
        request.cookies.update(
            {
                "user_id": user_id,
                "userId": user_id,
            }
        )
        headers = MutableHeaders(request.headers)
        request.scope.update(cookies=request.cookies)
        headers.update(
            {
                "userId": user_id,
                "cookies": json.dumps(request.cookies),
            }
        )
        request._headers = headers
        request.scope.update(headers=request.headers.raw)
        response.set_cookie("user_id", user_id, samesite="strict", httponly=True, secure=Services.SECURE_COOKIE)
        response.set_cookie("userId", user_id, samesite="strict", httponly=True, secure=Services.SECURE_COOKIE)
        response.set_cookie(
            "login-token",
            login_token,
            samesite="strict",
            httponly=True,
            secure=Services.SECURE_COOKIE,
            max_age=Secrets.LOCK_OUT_TIME_MINS * 60,
        )

    async def __call__(self, request: Request, response: Response) -> _AuthInfo:
        cookies = request.cookies
        login_token = cookies.get(self.cookie_name) or request.headers.get(self.cookie_name)
        if Services.SECURE_ACCESS:
            if not login_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            jwt_token = self.login_redis.get(login_token)
            if not jwt_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            try:
                user_id, new_token = self.token_validation(
                    token=jwt_token, login_token=login_token, host=request.client.host if request.client else "0.0.0.0"
                )
                await self.update_headers_and_cookies(request, response, user_id, new_token)
            except Exception as e:
                logging.exception(e)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ErrorMessages.UNKNOWN_ERROR,
                ) from e
            logging.debug(new_token)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token doesn't have required fields",
                )
            user_id = cookies.get("userId", request.headers.get("userId"))
            new_token = login_token
        else:
            user_id = cookies.get("userId", request.headers.get("userId"))
            new_token = login_token
        return _AuthInfo(
            user_id=user_id,
            ip_address=request.client.host if request.client else "0.0.0.0",  # type: ignore
            login_token=new_token,
            userId=user_id,
        )


CookieAuthentication = auth = _CookieAuthentication()
AuthInfo = Annotated[_AuthInfo, Depends(CookieAuthentication)]

__all__ = ["AuthInfo", "CookieAuthentication"]
