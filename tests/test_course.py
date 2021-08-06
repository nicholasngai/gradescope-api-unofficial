import unittest

from gradescope import Client, Course

from . import utils

class TestCourse(unittest.TestCase):
    @utils.with_login_client
    @utils.with_course(217765) # GSAPI 101.
    def test_instructor_course(self, client: Client, course: Course) -> None:
        self.assertEqual(course.id, 217765, 'Incorrect course ID')
        self.assertEqual(course.get_short_name(), 'GSAPI 101',
                         'Incorrect course short name')
        self.assertEqual(course.get_name(), 'Gradescope API Automated Testing Bed',
                         'Incorrect course name')
        self.assertEqual(course.get_term(), 'Fall 2020', 'Incorrect course term')
        self.assertTrue(course.is_instructor, 'Should be instructor')

    @utils.with_login_client
    @utils.with_course(217813) # GSAPI 103.
    def test_student_course(self, client: Client, course: Course) -> None:
        self.assertEqual(course.get_short_name(), 'GSAPI 103',
                         'Incorrect course short name')
        self.assertEqual(course.get_name(), 'Gradescope API Automated Testing Bed',
                         'Incorrect course name')
        self.assertEqual(course.get_term(), 'Fall 2020', 'Incorrect course term')
        self.assertFalse(course.is_instructor, 'Should not be instructor')

    @utils.with_login_client
    @utils.with_course(217765) # GSAPI 101.
    def test_student_course_description(self, client: Client,
                                        course: Course) -> None:
        self.assertEqual(course.get_description(),
                         'A description for GSAPI 101.',
                         'Incorrect course description')

    @utils.with_login_client
    @utils.with_course(217813) # GSAPI 103.
    def test_instructor_course_description(self, client: Client,
                                           course: Course) -> None:
        self.assertEqual(course.get_description(),
                         'A description for GSAPI 103.',
                         'Incorrect course description')

    @utils.with_login_client
    @utils.with_course(217765) # GSAPI 101.
    def test_assignment_list(self, client: Client, course: Course) -> None:
        assignments = course.get_assignments()
        assignment_ids = [assignment.id for assignment in assignments]
        self.assertIn(910142, assignment_ids, 'Missing Test Homework')
        self.assertIn(910133, assignment_ids, 'Missing Test Exam')
        self.assertIn(910152, assignment_ids, 'Missing Test Online Homework')
        self.assertIn(910153, assignment_ids, 'Missing Test Online Exam')

    @utils.with_login_client
    def test_invalid_course(self, client: Client) -> None:
        course = client.fetch_course(1) # Some invalid course ID.
        self.assertIsNone(course)
