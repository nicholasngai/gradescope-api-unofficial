from __future__ import annotations

import re
from types import TracebackType
from typing import Any, List, Optional

import lxml.html
import requests

from . import endpoints
from .course import Course

DOMAIN = 'www.gradescope.com'

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

    def log_out(self) -> None:
        """Logs out of Gradescope. Must be logged in to call this function."""
        self._assert_logged_in()
        self._get(endpoints.LOGOUT, allow_redirects=False)
        self.logged_in = False

    def fetch_course_list(self) -> List[Course]:
        """Fetches the list of courses the client is enrolled in or teaches.

        :returns: A list of courses the client is enrolled in or teaches.
        :rtype: list[Course]
        """
        self._assert_logged_in()

        res = self._get(endpoints.HOME)
        html = lxml.html.fromstring(res.text)

        courses: List[Course] = []

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
                match = re.match('/courses/(\d+)', href)
                assert match is not None, "Can't extract course ID from href"
                course_id = int(match.groups(1)[0])
                courses.append(Course(self, course_id, short_name, name, term))

        return courses

    def fetch_course(self, course_id: int) -> Optional[Course]:
        """Fetches the course with the given ID. Returns None if not
        accessible.

        :param course_id: The ID of the course.
        :type course_id: int
        :returns: The course, if found.
        :rtype: Optional[Course]
        """
        self._assert_logged_in()

        res = self._get(endpoints.HOME)
        html = lxml.html.fromstring(res.text)

        # Get course.
        term_elems = html.xpath(f'//*[contains(@class,"courseList--term") and //a[contains(@href,"/courses/{course_id}")]]')
        if len(term_elems) == 0:
            # Course was not found.
            return None
        term_elem = term_elems[0]
        term = term_elem.xpath('text()')[0]
        course_box_elem = term_elem.xpath('following-sibling::*[contains(@class,"courseList--coursesForTerm")]'
                                '//a[contains(@class,"courseBox")]')[0]
        short_name = course_box_elem.xpath('*[contains(@class,"courseBox--shortname")]/text()')[0]
        name = course_box_elem.xpath('*[contains(@class,"courseBox--name")]/text()')[0]

        return Course(self, course_id, short_name, name, term)

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

    def _assert_logged_in(self) -> None:
        assert self.logged_in, 'Client must be logged in'

    def __enter__(self) -> Client:
        return self

    def __exit__(self, exc_type: Optional[Exception], exc_val: Any,
                 exc_tb: Optional[TracebackType]) -> None:
        if self.logged_in:
            self.log_out()
        self._session.__exit__()
