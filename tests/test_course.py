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
        for course in course_list:
            if course.course_id == 217765 \
                    and course.short_name == 'GSAPI 101' \
                    and course.name == 'Gradescope API Automated Testing Bed' \
                    and course.term == 'Fall 2020':
                course101_found = True
            elif course.course_id == 217774 \
                    and course.short_name == 'GSAPI 102' \
                    and course.name == 'Gradescope API Automated Testing Bed' \
                    and course.term == 'Fall 2020':
                course102_found = True
            elif course.course_id == 217813 \
                    and course.short_name == 'GSAPI 103' \
                    and course.name == 'Gradescope API Automated Testing Bed' \
                    and course.term == 'Fall 2020':
                course103_found = True
        self.assertTrue(course101_found, 'Missing GSAPI 101')
        self.assertTrue(course102_found, 'Missing GSAPI 102')
        self.assertTrue(course103_found, 'Missing GSAPI 103')

    @utils.with_login_client
    def test_fetch_course(self, client: Client) -> None:
        course = client.fetch_course(217765) # GSAPI 101.
        self.assertIsNotNone(course)
        assert course is not None # Hint to type checker.
        self.assertTrue(course.course_id == 217765 \
                            and course.short_name == 'GSAPI 101' \
                            and course.name == 'Gradescope API Automated Testing Bed' \
                            and course.term == 'Fall 2020',
                        f'Incorrect course; got: {course}')

    @utils.with_login_client
    def test_fetch_invalid_course(self, client: Client) -> None:
        course = client.fetch_course(1) # Some invalid course ID.
        self.assertIsNone(course)
