import unittest

from gradescope import Client

from . import utils

class TestAssignment(unittest.TestCase):
    @utils.with_login_client
    def test_assignment_list(self, client: Client) -> None:
        course = client.fetch_course(217765) # GSAPI 101.
        self.assertIsNotNone(course)
        assert course is not None # Hint to type checker.
        assignments = course.fetch_assignments()
        homework_found = False
        exam_found = False
        online_homework_found = False
        online_exam_found = False
        for assignment in assignments:
            if assignment.assignment_id == 910142 \
                    and assignment.name == 'Test Homework':
                homework_found = True
            elif assignment.assignment_id == 910133 \
                    and assignment.name == 'Test Exam':
                exam_found = True
            elif assignment.assignment_id == 910152 \
                    and assignment.name == 'Test Online Homework':
                online_homework_found = True
            elif assignment.assignment_id == 910153 \
                    and assignment.name == 'Test Online Exam':
                online_exam_found = True
        self.assertTrue(homework_found, 'Missing Test Homework')
        self.assertTrue(exam_found, 'Missing Test Exam')
        self.assertTrue(online_homework_found, 'Missing Test Online Homework')
        self.assertTrue(online_exam_found, 'Missing Test Online Exam')
