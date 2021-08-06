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
    @utils.with_course(217765) # GSAPI 101.
    def test_fetch_instructor_course(self, client: Client,
                                     course: Course) -> None:
        self.assertEqual(course.course_id, 217765, 'Incorrect course ID')
        self.assertEqual(course.short_name, 'GSAPI 101',
                         'Incorrect course short name')
        self.assertEqual(course.name, 'Gradescope API Automated Testing Bed',
                         'Incorrect course name')
        self.assertEqual(course.term, 'Fall 2020', 'Incorrect course term')
        self.assertTrue(course.is_instructor, 'Should be instructor')

    @utils.with_login_client
    @utils.with_course(217813) # GSAPI 103.
    def test_fetch_student_course(self, client: Client, course: Course) -> None:
        self.assertEqual(course.short_name, 'GSAPI 103',
                         'Incorrect course short name')
        self.assertEqual(course.name, 'Gradescope API Automated Testing Bed',
                         'Incorrect course name')
        self.assertEqual(course.term, 'Fall 2020', 'Incorrect course term')
        self.assertFalse(course.is_instructor, 'Should not be instructor')

    @utils.with_login_client
    @utils.with_course(217765) # GSAPI 101.
    def test_fetch_student_course_description(self, client: Client,
                                              course: Course) -> None:
        self.assertEqual(course.get_description(),
                         'A description for GSAPI 101.',
                         'Incorrect course description')

    @utils.with_login_client
    @utils.with_course(217813) # GSAPI 103.
    def test_fetch_instructor_course_description(self, client: Client,
                                                 course: Course) -> None:
        self.assertEqual(course.get_description(),
                         'A description for GSAPI 103.',
                         'Incorrect course description')

    @utils.with_login_client
    def test_fetch_invalid_course(self, client: Client) -> None:
        course = client.fetch_course(1) # Some invalid course ID.
        self.assertIsNone(course)
