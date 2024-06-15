import logging
from abc import abstractmethod
from urllib.parse import urlparse

import httpx

from tp_auth_jwt.exceptions import CustomError

from .security_pydantic import Secrets
from .token_creation import create_token


class AuthenticationError(Exception): ...


class ForbiddenError(Exception): ...


token = ""
secrets = {}

NOT_AUTHORIZED = "Not authorized"
NOT_PERMITTED = "Not Permitted"


class HTTPXRequestHandler:
    def __init__(self, url, time_out=None) -> None:
        self.time_out = time_out
        self.url = url
        self.verify = False

    @property
    def get_timeout(self):
        return self.time_out

    def delete(self, path="", json=None, data=None, update_args=True, **kwargs) -> httpx.Response:
        url = self.get_url(path)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        with httpx.Client(verify=custom_args.pop("verify", False), cookies=cookies, headers=headers) as client:
            response = client.delete(url=url, data=data, json=json, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)

        if update_args:
            self.update_args(response=response)
        return response

    def put(self, path="", json=None, data=None, update_args=True, **kwargs) -> httpx.Response:
        url = self.get_url(path)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        with httpx.Client(verify=custom_args.pop("verify", False), cookies=cookies, headers=headers) as client:
            response = client.put(url=url, data=data, json=json, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)

        if update_args:
            self.update_args(response=response)
        return response

    def post(self, path="", json=None, data=None, update_args=True, **kwargs) -> httpx.Response:
        """
        The post function is a wrapper around the httpx.Client().post() function.
        It takes in all of the same arguments as httpx.Client().post(), but also includes
        the path argument, which allows you to specify a relative URL for your request, and
        update_args, which will update self._args with any new data returned from the server.

        :param self: Represent the instance of the class
        :param path: Specify the path of the url
        :param json: Send a json body to the server
        :param data: Send data to the server
        :param update_args: Update the arguments in the response
        :param **kwargs: Pass in keyword arguments to the function
        :return: A response object

        """
        """doc"""
        url = self.get_url(path)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        with httpx.Client(verify=custom_args.pop("verify", False), cookies=cookies, headers=headers) as client:
            response = client.post(url=url, data=data, json=json, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)

        if update_args:
            self.update_args(response=response)
        return response

    def get(self, path="", params=None, **kwargs) -> httpx.Response:
        """
        The get function is a wrapper around the httpx.Client().get() function.
        It takes in a path and params, which are used to construct the url for the request.
        The kwargs are passed into self.prepare_args(), which returns a dictionary of arguments that will be passed into httpx's get function.

        :param self: Represent the instance of the class
        :param path: Specify the path of the api endpoint
        :param params: Pass the parameters to the api
        :param **kwargs: Pass a variable number of keyword arguments to the function
        :return: A requests

        """
        """doc"""
        url = self.get_url(path)
        # Commenting this as currently there is no use case for this
        # self.update_args(response = response)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        with httpx.Client(verify=custom_args.pop("verify", False), cookies=cookies, headers=headers) as client:
            response = client.get(url=url, params=params, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)
        return response

    async def async_delete(self, path="", json=None, data=None, update_args=True, **kwargs) -> httpx.Response:
        url = self.get_url(path)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        async with httpx.AsyncClient(
            verify=custom_args.pop("verify", False), cookies=cookies, headers=headers
        ) as client:
            response = await client.delete(url=url, data=data, json=json, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)

        if update_args:
            self.update_args(response=response)
        return response

    async def async_put(self, path="", json=None, data=None, update_args=True, **kwargs) -> httpx.Response:
        url = self.get_url(path)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        async with httpx.AsyncClient(
            verify=custom_args.pop("verify", False), cookies=cookies, headers=headers
        ) as client:
            response = await client.put(url=url, data=data, json=json, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)

        if update_args:
            self.update_args(response=response)
        return response

    async def async_post(self, path="", json=None, data=None, update_args=True, **kwargs) -> httpx.Response:
        """
        The post function is a wrapper around the httpx.Client().post() function.
        It takes in all of the same arguments as httpx.Client().post(), but also includes
        the path argument, which allows you to specify a relative URL for your request, and
        update_args, which will update self._args with any new data returned from the server.

        :param self: Represent the instance of the class
        :param path: Specify the path of the url
        :param json: Send a json body to the server
        :param data: Send data to the server
        :param update_args: Update the arguments in the response
        :param **kwargs: Pass in keyword arguments to the function
        :return: A response object

        """
        """doc"""
        url = self.get_url(path)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        async with httpx.AsyncClient(
            verify=custom_args.pop("verify", False), cookies=cookies, headers=headers
        ) as client:
            response = await client.post(url=url, data=data, json=json, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)

        if update_args:
            self.update_args(response=response)
        return response

    async def async_get(self, path="", params=None, **kwargs) -> httpx.Response:
        """
        The get function is a wrapper around the httpx.Client().get() function.
        It takes in a path and params, which are used to construct the url for the request.
        The kwargs are passed into self.prepare_args(), which returns a dictionary of arguments that will be passed into httpx's get function.

        :param self: Represent the instance of the class
        :param path: Specify the path of the api endpoint
        :param params: Pass the parameters to the api
        :param **kwargs: Pass a variable number of keyword arguments to the function
        :return: A requests

        """
        """doc"""
        url = self.get_url(path)
        # Commenting this as currently there is no use case for this
        # self.update_args(response = response)
        logging.info(url)
        custom_args = self.prepare_args(**kwargs)
        headers = custom_args.pop("headers", None)
        cookies = custom_args.pop("cookies", None)
        async with httpx.AsyncClient(
            verify=custom_args.pop("verify", False), cookies=cookies, headers=headers
        ) as client:
            response = await client.get(url=url, params=params, **custom_args)

        if response.status_code == 401:
            raise AuthenticationError(NOT_AUTHORIZED)

        if response.status_code == 403:
            raise ForbiddenError(NOT_PERMITTED)
        return response

    def get_url(self, path):
        if path:
            return f"{self.url.rstrip('/')}/{path.lstrip('/').rstrip('/')}"
        return self.url.rstrip("/")

    def verify_request(self):
        if self.url_scheme(self.url) == "https":
            self.verify = True
        return self.verify

    @staticmethod
    def url_scheme(url):
        return urlparse(url).scheme

    @abstractmethod
    def prepare_args(self, **kwargs): ...

    @abstractmethod
    def update_args(self, **kwargs): ...


class AuthRequest(HTTPXRequestHandler):
    """
    Utility to use prismatica API's Directly
    """

    def __init__(self, url, user_id: str = None, time_out=None) -> None:
        super().__init__(url, time_out=time_out)
        self.user_id = user_id

    def prepare_args(self, **kwargs) -> dict:
        """
        The prepare_args function is used to prepare the arguments for a request.
            It takes in keyword arguments and returns a dictionary of prepared args.


        :param self: Represent the instance of the class
        :param **kwargs: Pass a variable number of keyword arguments to the function
        :return: A dictionary with the following keys:

        """
        post_args = {} | kwargs
        post_args |= {"headers": self.get_headers(**kwargs, user_id=self.user_id)}
        post_args |= {"timeout": self.get_timeout}
        post_args |= {"verify": self.verify_request()}
        post_args |= {"cookies": self.get_cookies(**post_args, user_id=self.user_id)}
        cookies = post_args.get("cookies", {})
        post_args["cookies"] = {k: v for k, v in cookies.items() if v is not None}
        headers = post_args.get("headers", {})
        post_args["headers"] = {k: v for k, v in headers.items() if v is not None}
        return post_args

    def update_args(self, **kwargs) -> bool:
        """
        The update_args function is used to update the token in the header of each request.
            This function will be called before every request and will check if a new token has been returned.
            If so, it updates the global variable 'token' with this new value.

        :param self: Represent the instance of the class
        :param **kwargs: Pass in a dictionary of arguments to the function
        :return: A boolean value

        """
        data = kwargs.get("response").headers.get("token")
        if data:
            global token
            token = data
        return data

    def get_headers(self, **kwargs) -> dict:
        """
        The get_headers function is used to create a dictionary of headers that will be sent with every request.
            The function takes in an optional keyword argument 'headers' which can be used to add additional headers.
            This allows the user to override any header set by default.

        :param self: Represent the instance of the class
        :param **kwargs: Pass keyworded, variable-length argument list to a function
        :return: A dictionary

        """
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Cache-Control": "no-store",
        }
        if self.user_id:
            headers["userId"] = self.user_id
        headers |= kwargs.get("headers", {})
        if not headers.get("login-token"):
            headers |= {"login-token": AuthRequest.create_token(user_id=kwargs.get("user_id"))}
        return headers

    @staticmethod
    def get_cookies(**kwargs) -> dict:
        """
        The get_cookies function returns a dictionary of cookies.


        :param **kwargs: Collect all the keyword arguments passed to a function
        :return: A dictionary of cookies

        """
        cookies = {"userId": kwargs.get("user_id")}
        cookies |= kwargs.get("cookies", {})
        cookies["login-token"] = kwargs.get("headers", {}).get("login-token")
        return cookies

    @staticmethod
    def create_token(host: str = "127.0.0.1", user_id=None, internal_token=Secrets.TOKEN):
        """
        The create_token function creates a token for the user to use in their requests.


        :param host: str: Set the host ip address
        :param user_id: Identify the user
        :param internal_token: Create a token
        :param project_id: str: Identify the project id
        :return: A token

        """
        """
        This method is to create a cookie
        """

        try:
            user_id = user_id or "user_099"
            return create_token(
                user_id=user_id,
                ip=host,
                token=internal_token,
            )
        except Exception as e:
            raise CustomError(f"{str(e)}") from e
