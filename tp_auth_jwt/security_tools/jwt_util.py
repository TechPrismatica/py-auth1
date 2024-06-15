import logging
from pathlib import Path

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    MissingRequiredClaimError,
)

from tp_auth_jwt.exceptions import AuthenticationError, ErrorMessages
from tp_auth_jwt.security_tools.security_pydantic import PathConf, Secrets


class JWT:
    def __init__(self) -> None:
        self.max_login_age: int = Secrets.LOCK_OUT_TIME_MINS
        self.issuer: str = Secrets.ISSUER
        self.alg: str = Secrets.ALG
        self.public: Path = PathConf.KEY_PATH / "public"
        self.private: Path = PathConf.KEY_PATH / "private"

    def encode(self, payload) -> str:
        try:
            if not self.public.is_file() or not self.private.is_file():
                raise FileNotFoundError("Key pair for login is not available. Please check configuration.")
            key = Path(self.private).read_text()
            return jwt.encode(payload, key, algorithm=self.alg)
        except Exception as e:
            logging.exception(f"Exception while encoding JWT: {str(e)}")
            raise

    def decode(self, token):
        try:
            if not self.public.is_file() or not self.private.is_file():
                raise FileNotFoundError("Key pair for login is not available. Please check configuration.")
            key = Path(self.public).read_text()
            return jwt.decode(token, key, algorithms=self.alg)
        except Exception as e:
            logging.exception(f"Exception while decoding JWT: {str(e)}")
            raise

    def validate(self, token):
        if not self.public.is_file() or not self.private.is_file():
            raise FileNotFoundError("Key pair for login is not available. Please check configuration.")
        key = Path(self.public).read_text()
        try:
            return jwt.decode(
                token,
                key,
                algorithms=self.alg,
                leeway=Secrets.LEEWAY_IN_MINS,
                options={"require": ["exp", "iss"]},
            )

        except InvalidSignatureError as e:
            raise AuthenticationError(ErrorMessages.ERROR003) from e
        except ExpiredSignatureError as e:
            raise AuthenticationError(ErrorMessages.ERROR002) from e
        except MissingRequiredClaimError as e:
            raise AuthenticationError(ErrorMessages.ERROR003) from e
        except Exception as e:
            logging.exception(f"Exception while validating JWT: {str(e)}")
            raise AuthenticationError(ErrorMessages.UNKNOWN_ERROR) from e

    def decode_custom_payload(self, token, key=Secrets.CUSTOM_SERVICE_KEY):
        if not self.public.is_file() or not self.private.is_file():
            raise FileNotFoundError("Key pair for login is not available. Please check configuration.")
        try:
            payload = jwt.decode(token, key, algorithms=["HS256"])
            return payload
        except Exception as e:
            logging.exception(f"Exception while decoding JWT: {str(e)}")
            raise
