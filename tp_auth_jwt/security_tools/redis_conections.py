from tp_redis_connector import RedisConnector

from tp_auth_jwt.security_tools.security_pydantic import (
    DatabaseConstants,
    Databases,
)

connector = RedisConnector(
    redis_uri=Databases.REDIS_URI, redis_type=Databases.REDIS_TYPE, master_service=Databases.REDIS_MASTER_SERVICE
)
login_db = connector.connect(db=DatabaseConstants.REDIS_LOGIN_DB, decode_responses=True)
