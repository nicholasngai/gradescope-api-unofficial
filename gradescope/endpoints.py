import string

BASE = 'https://www.gradescope.com'
HOME = BASE

LOGIN = f'{BASE}/login'
LOGOUT = f'{BASE}/logout'

COURSE = string.Template(f'{BASE}/courses/${{course_id}}')
COURSE_ASSIGNMENTS = string.Template(f'{COURSE.template}/assignments')
COURSE_EDIT = string.Template(f'{COURSE.template}/edit')

ASSIGNMENT = string.Template(f'{COURSE_ASSIGNMENTS.template}/${{assignment_id}}')
ASSIGNMENT_EDIT = string.Template(f'{ASSIGNMENT.template}/edit')
