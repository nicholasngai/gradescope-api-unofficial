import unittest

from gradescope import Assignment, Client, Course

from . import utils

class TestAssignment(unittest.TestCase):
    @utils.with_login_client
    @utils.with_assignment_and_course(217765, 910133) # GSAPI 101, Exam.
    def test_exam_info(self, client: Client, course: Course,
                       assignment: Assignment) -> None:
        self.assertEqual(assignment.id, 910133, 'Incorrect assignment ID')
        self.assertEqual(assignment.get_name(), 'Test Exam',
                         'Incorrect assignment name')
        self.assertEqual(assignment.get_type(), Assignment.Type.EXAM,
                         'Incorrect assignment type')

    @utils.with_login_client
    @utils.with_assignment_and_course(217765, 910142) # GSAPI 101, Homework.
    def test_homework_info(self, client: Client, course: Course,
                           assignment: Assignment) -> None:
        self.assertEqual(assignment.id, 910142, 'Incorrect assignment ID')
        self.assertEqual(assignment.get_name(), 'Test Homework',
                         'Incorrect assignment name')
        self.assertEqual(assignment.get_type(), Assignment.Type.HOMEWORK,
                         'Incorrect assignment type')

    @utils.with_login_client
    @utils.with_assignment_and_course(217765, 1400964) # GSAPI 101, Bubble Sheet.
    def test_bubble_sheet_info(self, client: Client, course: Course,
                               assignment: Assignment) -> None:
        self.assertEqual(assignment.id, 1400964, 'Incorrect assignment ID')
        self.assertEqual(assignment.get_name(), 'Test Bubble Sheet',
                         'Incorrect assignment name')
        self.assertEqual(assignment.get_type(), Assignment.Type.BUBBLE_SHEET,
                         'Incorrect assignment type')

    @utils.with_login_client
    @utils.with_assignment_and_course(217765, 1400962) # GSAPI 101, Programming.
    def test_programming_info(self, client: Client, course: Course,
                              assignment: Assignment) -> None:
        self.assertEqual(assignment.id, 1400962, 'Incorrect assignment ID')
        self.assertEqual(assignment.get_name(), 'Test Programming Assignment',
                         'Incorrect assignment name')
        self.assertEqual(assignment.get_type(), Assignment.Type.PROGRAMMING,
                         'Incorrect assignment type')

    @utils.with_login_client
    @utils.with_assignment_and_course(217765, 910152) # GSAPI 101, Online.
    def test_online_info(self, client: Client, course: Course,
                         assignment: Assignment) -> None:
        self.assertEqual(assignment.id, 910152, 'Incorrect assignment ID')
        self.assertEqual(assignment.get_name(), 'Test Online Homework',
                         'Incorrect assignment name')
        self.assertEqual(assignment.get_type(), Assignment.Type.ONLINE,
                         'Incorrect assignment type')
