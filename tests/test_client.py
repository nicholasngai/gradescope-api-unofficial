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

