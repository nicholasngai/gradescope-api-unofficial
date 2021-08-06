import functools
import os
from typing import Callable, TypeVar
import unittest

from gradescope import Assignment, Client, Course

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
        @functools.wraps(func)
        def wrapper(self: T, client: Client) -> None:
            course = client.fetch_course(course_id)
            self.assertIsNotNone(course,
                                 f'Failed to get course by ID: {course_id}')
            assert course is not None # Hint to type checker.
            func(self, client, course)
        return wrapper
    return with_course_decorator

def with_assignment_and_course(course_id: int, assignment_id: int) \
        -> Callable[[Callable[[T, Client, Course, Assignment], None]], Callable[[T, Client], None]]:
    def with_assignment_and_course_decorator(func: Callable[[T, Client, Course, Assignment], None]) \
            -> Callable[[T, Client], None]:
        @functools.wraps(func)
        @with_course(course_id)
        def wrapper(self: T, client: Client, course: Course) -> None:
            assignment = course.get_assignment(assignment_id)
            self.assertIsNotNone(assignment,
                                 f'Failed to get assignment by ID: {assignment_id}')
            assert assignment is not None # Hint to the type checker.
            func(self, client, course, assignment)
        return wrapper
    return with_assignment_and_course_decorator
