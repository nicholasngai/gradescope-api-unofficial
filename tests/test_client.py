import os
import unittest

from gradescope import Client, GSInvalidRequestException

from . import utils

class TestClient(unittest.TestCase):
    @utils.with_login_client
    def test_login(self, client: Client) -> None:
        """Tests a successful login to Gradescope with valid credentials
        provided in GSAPI_USERNAME and GSAPI_PASSWORD enviornment variables.
        Login functionality is handled by the shared decorator, so no actual
        code is needed.
        """
        pass

    def test_login_invalid(self) -> None:
        """Tests a failed login because of invalid credentials."""
        with self.assertRaises(GSInvalidRequestException,
                msg='Login was successful with invalid credentials'):
            with Client('invalid@example.com', 'credentials') as client:
                pass

    @utils.with_login_client
    def test_fetch_course_list(self, client: Client) -> None:
        course_list = client.fetch_course_list()
        course_ids = [course.id for course in course_list]
        self.assertIn(217765, course_ids, 'Missing GSAPI 101')
        self.assertIn(217765, course_ids, 'Missing GSAPI 102')
        self.assertIn(217813, course_ids, 'Missing GSAPI 103')
