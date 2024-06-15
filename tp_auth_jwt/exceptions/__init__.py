class QueryFormationError(Exception):
    """raises when there is an issue in Query formation"""


class CustomError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class ErrorMessages:
    UNKNOWN = "Unknown Error occurred"
    ERR001 = "Configurations not available, please verify the database."
    ERR002 = "Data Not Found"
    UNKNOWN_ERROR = "Error occurred while processing your request."
    ERROR001 = "Authentication Failed. Please verify token"
    ERROR002 = "Signature Expired"
    ERROR003 = "Signature Not Valid"
