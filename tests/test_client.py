import os
import unittest

from gradescope import Client

class TestClient(unittest.TestCase):
    @unittest.skipIf('GSAPI_USERNAME' not in os.environ
                            or 'GSAPI_PASSWORD' not in os.environ,
                     'No test login provided')
    def test_login(self) -> None:
        """Tests a successful login to Gradescope with valid credentials
        provided in GSAPI_USERNAME and GSAPI_PASSWORD enviornment variables.
        """
        username = os.environ['GSAPI_USERNAME']
        password = os.environ['GSAPI_PASSWORD']
        with Client() as client:
            res = client.log_in(username, password)
            self.assertTrue(res, 'Login was not successful with credentials')

    def test_login_invalid(self) -> None:
        """Tests a failed login because of invalid credentials."""
        with Client() as client:
            res = client.log_in('invalid@example.com', 'credentials')
            self.assertFalse(res,
                             'Login was successful with invalid credentials')
