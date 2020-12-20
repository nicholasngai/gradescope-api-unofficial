import functools
import os
from typing import Callable, TypeVar
import unittest

from gradescope import Client

T = TypeVar('T', bound=unittest.TestCase)

def with_login_client(func: Callable[[T, Client], None]):
    @unittest.skipIf('GSAPI_USERNAME' not in os.environ
                            or 'GSAPI_PASSWORD' not in os.environ,
                     'No test login provided')
    @functools.wraps(func)
    def wrapper(self: T) -> None:
        username = os.environ['GSAPI_USERNAME']
        password = os.environ['GSAPI_PASSWORD']
        with Client() as client:
            self.assertTrue(client.log_in(username, password),
                            'Login was not successful with credentials')
            func(self, client)
    return wrapper
