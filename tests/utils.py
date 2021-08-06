import functools
import os
from typing import Callable, TypeVar
import unittest

from gradescope import Client, Course

T = TypeVar('T', bound=unittest.TestCase)

def with_login_client(func: Callable[[T, Client], None]) -> Callable[[T], None]:
    @unittest.skipIf('GSAPI_USERNAME' not in os.environ
                            or 'GSAPI_PASSWORD' not in os.environ,
                     'No test login provided')
    @functools.wraps(func)
    def wrapper(self: T) -> None:
        username = os.environ['GSAPI_USERNAME']
        password = os.environ['GSAPI_PASSWORD']
        with Client(username, password) as client:
            func(self, client)
    return wrapper

def with_course(course_id: int) \
        -> Callable[[Callable[[T, Client, Course], None]],
                    Callable[[T, Client], None]]:
    def with_course_decorator(func: Callable[[T, Client, Course], None]) \
            -> Callable[[T, Client], None]:
        def wrapper(self: T, client: Client) -> None:
            course = client.fetch_course(course_id)
            self.assertIsNotNone(course)
            assert course is not None # Hint to type checker.
            func(self, client, course)
        return wrapper
    return with_course_decorator
