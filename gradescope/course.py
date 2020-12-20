from dataclasses import dataclass

@dataclass(frozen=True)
class CourseReference:
    course_id: int
    short_name: str
    name: str
    term: str
    num_assignments: int

class Course(CourseReference):
    pass
