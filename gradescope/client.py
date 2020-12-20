from __future__ import annotations

import functools
import re
import traceback
from types import TracebackType
from typing import Any, Callable, List, Optional, TypeVar

import lxml.html
import requests

from . import endpoints
from .course import Course, CourseReference

DOMAIN = 'www.gradescope.com'

T = TypeVar('T')

def _must_be_logged_in(func: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(func)
    def wrapper(self: Client, *args, **kwargs) -> T:
        assert self.logged_in, 'Client must be logged in'
        return func(self, *args, **kwargs)
    return wrapper

class Client:
    def __init__(self) -> None:
        self.logged_in = False

        self._session = requests.Session()
        self._csrf_token: Optional[str] = None

    def log_in(self, username: str, password: str) -> bool:
        """Logs into Gradescope with the given credentials.

        :param username: The username.
        :type username: str
        :param password: The password.
        :type password: str
        :returns: Whether the login was successful.
        :rtype: bool
        """
        assert not self.logged_in, 'Client is already logged in'

        # Get an authenticity token (separate from a CSRF token).
        res = self._get(endpoints.LOGIN)
        html = lxml.html.fromstring(res.text)
        authenticity_token = \
                html.xpath('//input[@name="authenticity_token"]/@value')[0]
        res = self._post(endpoints.LOGIN, data={
            'authenticity_token': authenticity_token,
            'session[email]': username,
            'session[password]': password
        }, allow_redirects=False)

        # Return whether 'signed_token' is now a cookie we have.
        success = self._session.cookies.get('signed_token', domain=DOMAIN) \
                is not None
        if success:
            self.logged_in = True
        return success

    @_must_be_logged_in
    def log_out(self) -> None:
        self._get(endpoints.LOGOUT, allow_redirects=False)
        self.logged_in = False

    @_must_be_logged_in
    def fetch_course_list(self) -> List[CourseReference]:
        res = self._get(endpoints.HOME)
        html = lxml.html.fromstring(res.text)

        course_refs: List[CourseReference] = []

        # Get courses.
        term_elems = html.xpath('//*[contains(@class,"courseList--term")]')
        for term_elem in term_elems:
            term = term_elem.xpath('text()')[0]
            course_box_elems = term_elem.xpath('following-sibling::*[contains(@class,"courseList--coursesForTerm")]'
                                               '//a[contains(@class,"courseBox")]')
            for course_box_elem in course_box_elems:
                href = course_box_elem.xpath('@href')[0]
                short_name = course_box_elem.xpath('*[contains(@class,"courseBox--shortname")]/text()')[0]
                name = course_box_elem.xpath('*[contains(@class,"courseBox--name")]/text()')[0]
                assignments_text = course_box_elem.xpath('*[contains(@class,"courseBox--assignments")]/text()')[0]
                match = re.match('/courses/(\d+)', href)
                assert match is not None, "Can't extract course ID from href"
                course_id = int(match.groups(1)[0])
                match = re.match('(\d+) assignments?', assignments_text)
                assert match is not None, "Can't extract assignments from text"
                num_assignments = int(match.groups(1)[0])
                course_refs.append(CourseReference(course_id, short_name, name,
                                                   term, num_assignments))

        return course_refs

    def _get(self, *args, **kwargs) -> requests.Response:
        """Makes a GET request with the session, saving any CSRF token that is
        returned.
        """
        res = self._session.get(*args, **kwargs)
        # TODO Extract CSRF token if present.
        return res

    def _post(self, *args, **kwargs) -> requests.Response:
        """Makes a POST request with the session, saving any CSRF token that is
        returned.
        """
        res = self._session.post(*args, **kwargs)
        # TODO Extract CSRF token if present.
        return res

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type: Optional[Exception], exc_val: Any,
                 exc_tb: Optional[TracebackType]) -> None:
        if self.logged_in:
            self.log_out()
        self._session.__exit__()
