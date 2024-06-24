from datetime import datetime, timedelta
import logging

import jwt

from tp_auth.config import Secrets, SupportedAlgorithms


class JWTUtil:
    def __init__(self, algorithm: SupportedAlgorithms = None, write_key: str = None, read_key: str = None) -> None:
        self.algorithm = algorithm or Secrets.algorithm
        if self.algorithm == SupportedAlgorithms.RS256:
            self.read_key = read_key or Secrets.public_key
            if Secrets.authorization_server or write_key:
                self.write_key = write_key or Secrets.private_key
            else:
                self.write_key = None
        elif self.algorithm == SupportedAlgorithms.HS256:
            self.read_key = read_key or Secrets.secret_key
            self.write_key = write_key or Secrets.secret_key

    def encode(self, payload: dict) -> str:
        try:
            payload |= {"iss": Secrets.issuer, "exp": datetime.utcnow() + timedelta(minutes=Secrets.expiry)}
            return jwt.encode(payload, self.write_key, algorithm=self.algorithm)
        except Exception as e:
            logging.error(f"Error encoding token: {e}")
            raise e

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.read_key, algorithms=[self.algorithm])
        except Exception as e:
            logging.error(f"Error decoding token: {e}")
            raise e

    def verify(self, token: str) -> bool:
        try:
            jwt.decode(token, self.read_key, algorithms=[self.algorithm])
            return True
        except jwt.InvalidSignatureError as e:
            logging.error(f"Invalid signature: {e}")
            return False
        except jwt.ExpiredSignatureError as e:
            logging.error(f"Expired signature: {e}")
            return False
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid token: {e}")
            return False
        except Exception as e:
            logging.error(f"Error verifying token: {e}")
            raise e
