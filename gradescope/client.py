from __future__ import annotations

import traceback
from types import TracebackType
from typing import Any, Optional

import lxml.html
import requests

from . import endpoints

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
        assert self.logged_in, 'Client is not logged in'
        self._get(endpoints.LOGOUT, allow_redirects=False)
        self.logged_in = False

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
