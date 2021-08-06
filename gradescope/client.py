from __future__ import annotations

import re
from types import TracebackType
from typing import Any, List, Optional

import lxml.html
import requests

from . import endpoints
from .course import Course
from .error import GSInvalidRequestException
from .term import Term

DOMAIN = 'www.gradescope.com'

class Client:
    def __init__(self, username: str, password: str) -> None:
        """Constructs a Gradescope client with the given credentials.

        :param username: The username.
        :type username: str
        :param password: The password.
        :type password: str
        """
        self._session = requests.Session()
        self._csrf_token: Optional[str] = None

        if not self._log_in(username, password):
            raise GSInvalidRequestException('Invalid username or password')

    def _log_in(self, username: str, password: str) -> bool:
        """Logs into Gradescope with the given credentials.

        :param username: The username.
        :type username: str
        :param password: The password.
        :type password: str
        :returns: Whether the login was successful.
        :rtype: bool
        """
        # This is likely the first request, so use a _get call to store a CSRF
        # token.
        res = self._get(endpoints.LOGIN)
        res = self._post(endpoints.LOGIN, data={
            'session[email]': username,
            'session[password]': password
        }, allow_redirects=False)

        # Return whether 'signed_token' is now a cookie we have.
        success = self._session.cookies.get('signed_token', domain=DOMAIN) \
                is not None
        return success

    def log_out(self) -> None:
        """Logs out of Gradescope. Must be logged in to call this function."""
        self._get(endpoints.LOGOUT, allow_redirects=False)

    def fetch_course_list(self) -> List[Course]:
        """Fetches the list of courses the client is enrolled in or teaches.

        :returns: A list of courses the client is enrolled in or teaches.
        :rtype: list[Course]
        """
        res = self._get(endpoints.HOME)
        html = lxml.html.fromstring(res.text)

        courses: List[Course] = []

        # Get courses.
        # TODO We can check if we are instructor for a course here.
        term_elems = html.xpath('//*[contains(@class,"courseList--term")]')
        for term_elem in term_elems:
            term = Term.parse(term_elem.xpath('text()')[0])
            course_box_elems = term_elem.xpath('following-sibling::*[contains(@class,"courseList--coursesForTerm")]'
                                               '//a[contains(@class,"courseBox")]')
            for course_box_elem in course_box_elems:
                href = course_box_elem.xpath('@href')[0]
                short_name = course_box_elem.xpath('*[contains(@class,"courseBox--shortname")]/text()')[0]
                name = course_box_elem.xpath('*[contains(@class,"courseBox--name")]/text()')[0]
                match = re.search('/courses/(\d+)', href)
                assert match is not None, "Can't extract course ID from href"
                course_id = int(match.groups(1)[0])
                courses.append(Course(id=course_id, _client=self,
                                      _short_name=short_name, _name=name,
                                      _term=term))

        return courses

    def fetch_course(self, course_id: int) -> Optional[Course]:
        """Fetches the course with the given ID. Returns None if not
        accessible.

        :param course_id: The ID of the course.
        :type course_id: int
        :returns: The course, if found.
        :rtype: Optional[Course]
        """
        res = self._get(endpoints.HOME)
        html = lxml.html.fromstring(res.text)

        # Get course.
        # TODO We can check if we are instructor for a course here.
        course_box_elems = html.xpath(f'//a[contains(@href,"/courses/{course_id}")]')
        if len(course_box_elems) == 0:
            # Course was not found.
            return None
        course_box_elem = course_box_elems[0]
        short_name = course_box_elem.xpath('*[contains(@class,"courseBox--shortname")]/text()')[0]
        name = course_box_elem.xpath('*[contains(@class,"courseBox--name")]/text()')[0]
        term = Term.parse(course_box_elem.xpath('preceding::*[contains(@class,"courseList--term")][1]/text()')[0])

        return Course(id=course_id, _client=self, _short_name=short_name,
                      _name=name, _term=term)

    def _get(self, *args, **kwargs) -> requests.Response:
        """Makes a GET request with the session, saving any CSRF token that is
        returned.
        """
        # Default disallow redirects.
        kwargs.setdefault('allow_redirects', False)

        res = self._session.get(*args, **kwargs)
        # TODO Extract CSRF token if redirected.
        if res.headers['Content-Type'].startswith('text/html'):
            # Extract CSRF token from HTML.
            html = lxml.html.fromstring(res.text)
            tokens = html.xpath('//meta[@name="csrf-token"]/@content')
            if len(tokens) > 0:
                self._csrf_token = tokens[0]
        return res

    def _post(self, *args, **kwargs) -> requests.Response:
        """Makes a POST request with the session, saving any CSRF token that is
        returned.
        """
        # Default disallow redirects.
        kwargs.setdefault('allow_redirects', False)
        # Inject the CSRF token by default if not manually set (or data is not
        # present).
        kwargs['data'] = dict({ 'authenticity_token': self._csrf_token },
                              **kwargs.get('data', {}))

        res = self._session.post(*args, **kwargs)
        # TODO Extract CSRF token if redirected.
        if res.headers['Content-Type'].startswith('text/html'):
            # Extract CSRF token from HTML.
            html = lxml.html.fromstring(res.text)
            tokens = html.xpath('//meta[@name="csrf-token"]/@content')
            if len(tokens) > 0:
                self._csrf_token = tokens[0]
        return res

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type: Optional[Exception], exc_val: Any,
                 exc_tb: Optional[TracebackType]) -> None:
        self._session.__exit__()
