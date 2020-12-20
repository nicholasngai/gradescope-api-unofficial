import unittest

from gradescope import Client, Course

from . import utils

class TestCourse(unittest.TestCase):
    @utils.with_login_client
    def test_fetch_course_list(self, client: Client) -> None:
        course_list = client.fetch_course_list()
        course101_found = False
        course102_found = False
        course103_found = False
        for ref in course_list:
            if ref.course_id == 217765 and ref.short_name == 'GSAPI 101' \
                    and ref.name == 'Gradescope API Automated Testing Bed' \
                    and ref.term == 'Fall 2020' and ref.num_assignments == 0:
                course101_found = True
            elif ref.course_id == 217774 and ref.short_name == 'GSAPI 102' \
                    and ref.name == 'Gradescope API Automated Testing Bed' \
                    and ref.term == 'Fall 2020' and ref.num_assignments == 0:
                course102_found = True
            elif ref.course_id == 217813 and ref.short_name == 'GSAPI 103' \
                    and ref.name == 'Gradescope API Automated Testing Bed' \
                    and ref.term == 'Fall 2020' and ref.num_assignments == 0:
                course103_found = True
        self.assertTrue(course101_found, 'Missing GSAPI 101')
        self.assertTrue(course102_found, 'Missing GSAPI 102')
        self.assertTrue(course103_found, 'Missing GSAPI 103')
