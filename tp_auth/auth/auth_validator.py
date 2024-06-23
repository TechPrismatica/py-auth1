import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes
from typing_extensions import Annotated

from tp_auth.auth.user_specs import UserInfoSchema
from tp_auth.config import oauth2_scheme
from tp_auth.utilities.jwt_util import JWTUtil


class AuthValidator:
    def __init__(self, jwt_util: JWTUtil = None) -> None:
        self.jwt_utils = jwt_util or JWTUtil()

    async def __call__(
        self, security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> UserInfoSchema:
        if security_scopes.scopes:
            authenticate_value = f"Bearer scope={security_scopes.scope_str}"
        else:
            authenticate_value = "Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        try:
            payload = self.jwt_utils.decode(token)
            user_info = UserInfoSchema(**payload)
            available_scopes = user_info.scopes
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidSignatureError):
            raise credentials_exception
        for scope in security_scopes.scopes:
            if scope not in available_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return user_info


AuthValidatorInstance = AuthValidator()
UserInfo = Annotated[UserInfoSchema, Depends(AuthValidatorInstance)]

__all__ = ["AuthValidator", "UserInfo", "AuthValidatorInstance"]
