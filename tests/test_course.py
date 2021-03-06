import unittest

from gradescope import Client, Course, GSNotAuthorizedException, Term

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
        self.assertEqual(course.get_term(), Term(Term.Season.FALL, 2020),
                         'Incorrect course term')
        self.assertTrue(course.is_instructor, 'Should be instructor')

    @utils.with_login_client
    @utils.with_course(217813) # GSAPI 103.
    def test_student_course(self, client: Client, course: Course) -> None:
        self.assertEqual(course.get_short_name(), 'GSAPI 103',
                         'Incorrect course short name')
        self.assertEqual(course.get_name(), 'Gradescope API Automated Testing Bed',
                         'Incorrect course name')
        self.assertEqual(course.get_term(), Term(Term.Season.FALL, 2020),
                         'Incorrect course term')
        self.assertFalse(course.is_instructor, 'Should not be instructor')

    @utils.with_login_client
    def test_invalid_course(self, client: Client) -> None:
        course = client.fetch_course(1) # Some invalid course ID.
        self.assertIsNone(course)

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
    @utils.with_course(217774) # GSAPI 102. (Might be a different name.)
    def test_set_short_name(self, client: Client, course: Course) -> None:
        course.set_short_name('GSAPI 112')
        self.assertEqual(course.get_short_name(), 'GSAPI 112')
        course.set_short_name('GSAPI 102')
        self.assertEqual(course.get_short_name(), 'GSAPI 102')

    @utils.with_login_client
    @utils.with_course(217774) # GSAPI 102.
    def test_set_name(self, client: Client, course: Course) -> None:
        course.set_name('Gradescope API Changed Name')
        self.assertEqual(course.get_name(), 'Gradescope API Changed Name')
        course.set_name('Gradescope API Automated Testing Bed')
        self.assertEqual(course.get_name(),
                         'Gradescope API Automated Testing Bed')

    @utils.with_login_client
    @utils.with_course(217774) # GSAPI 102.
    def test_set_term(self, client: Client, course: Course) -> None:
        course.set_term(Term(Term.Season.FALL, 2020))
        self.assertEqual(course.get_term(), Term(Term.Season.FALL, 2020))
        course.set_term(Term(Term.Season.FALL, 2020))
        self.assertEqual(course.get_term(), Term(Term.Season.FALL, 2020))

    @utils.with_login_client
    @utils.with_course(217774) # GSAPI 102.
    def test_set_description(self, client: Client, course: Course) -> None:
        course.set_description('Changed description.')
        self.assertEqual(course.get_description(), 'Changed description.')
        course.set_description('')
        self.assertEqual(course.get_description(), '')

    @utils.with_login_client
    @utils.with_course(217813) # GSAPI 103.
    def test_student_attempt_update(self, client: Client,
                                    course: Course) -> None:
        with self.assertRaises(GSNotAuthorizedException):
            course.set_short_name('GSAPI 113')
        with self.assertRaises(GSNotAuthorizedException):
            course.set_name('Gradescope API Changed Name')
        with self.assertRaises(GSNotAuthorizedException):
            course.set_term(Term(Term.Season.SPRING, 2021))
        with self.assertRaises(GSNotAuthorizedException):
            course.set_description('Changed description.')

    @utils.with_login_client
    @utils.with_course(217765) # GSAPI 101.
    def test_assignment_list(self, client: Client, course: Course) -> None:
        assignments = course.get_assignments()
        assignment_ids = [assignment.id for assignment in assignments]
        self.assertIn(910142, assignment_ids, 'Missing Test Homework')
        self.assertIn(910133, assignment_ids, 'Missing Test Exam')
        self.assertIn(910152, assignment_ids, 'Missing Test Online Homework')
        self.assertIn(910153, assignment_ids, 'Missing Test Online Exam')
        self.assertIn(1400962, assignment_ids, 'Missing Test Bubble Sheet')
        self.assertIn(1400964, assignment_ids,
                      'Missing Test Programming Assignment')

    @utils.with_login_client
    @utils.with_course(217765) # GSAPI 101.
    def test_member_list(self, client: Client, course: Course) -> None:
        members = course.get_members()
        member_ids = [member.id for member in members]
        self.assertIn(9420701, member_ids,
                      'Missing Gradescope API Test Account')
        self.assertIn(9420657, member_ids, 'Missing Test Instructor')
        self.assertIn(12197620, member_ids, 'Missing Test Student')
