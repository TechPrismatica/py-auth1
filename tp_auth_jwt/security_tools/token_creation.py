import uuid
from datetime import datetime, timedelta, timezone

from tp_auth_jwt.exceptions import CustomError
from tp_auth_jwt.security_tools.jwt_util import JWT
from tp_auth_jwt.security_tools.redis_conections import login_db
from tp_auth_jwt.security_tools.security_pydantic import Secrets


def create_token(
    user_id,
    ip,
    token,
    age=Secrets.LOCK_OUT_TIME_MINS,
    login_token=None,
):
    """
    This method is to create a cookie
    """
    try:
        jwt = JWT()
        uid = login_token or str(uuid.uuid4()).replace("-", "")

        payload = {"ip": ip, "user_id": user_id, "token": token, "uid": uid, "age": age}
        exp = datetime.now(timezone.utc) + timedelta(minutes=age)
        _extras = {"iss": Secrets.ISSUER, "exp": exp}
        _payload = payload | _extras

        new_token = jwt.encode(_payload)
        login_db.set(uid, new_token)
        login_db.expire(uid, timedelta(minutes=age))

        return uid
    except Exception as e:
        raise CustomError(f"{str(e)}") from e
