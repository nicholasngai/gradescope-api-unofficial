from __future__ import annotations

from dataclasses import dataclass, field
import enum
import functools
from typing import Optional, TYPE_CHECKING

import lxml.html

from . import endpoints
from .error import GSInternalException, GSNotAuthorizedException

if TYPE_CHECKING:
    from .client import Client
    from .course import Course

# TODO I have no idea how to statically type this.
def _require_instructor(func):
    @functools.wraps(func)
    def wrapper(self: Assignment, *args, **kwargs):
        if not self._course.is_instructor:
            raise GSNotAuthorizedException(
                    'Must be instructor to execute this function')
        return func(*args, **kwargs)
    return wrapper

@dataclass
class Assignment:
    class Type(enum.Enum):
        """Instructor-uploaded PDF assignment."""
        EXAM = enum.auto()
        """Student-uploaded PDF assignment."""
        HOMEWORK = enum.auto()
        """Instructor- or student-uploaded Gradescope bubble sheets."""
        BUBBLE_SHEET = enum.auto()
        """Student-uploaded code assignments."""
        PROGRAMMING = enum.auto()
        """Student-inputted online assignment."""
        ONLINE = enum.auto()

    id: int
    _client: Client = field(repr=False, hash=False, compare=False)
    _course: Course = field(repr=False, hash=False, compare=False)

    _name: Optional[str] = field(default=None, repr=False, hash=False,
                                 compare=False)
    _type: Optional[Assignment.Type] = field(default=None, repr=False,
                                             hash=False, compare=False)

    def get_name(self, force: bool=False) -> str:
        """Returns the name of the assignment.

        :param force_update: If True, force an update instead of using the
        locally cached data.
        :type force_update: bool
        :returns: The assignment name.
        :rtype: str
        """
        if self._name is None or force:
            self._read_settings()
            assert self._name is not None, 'Error getting name from settings'
        return self._name

    def get_type(self) -> Assignment.Type:
        """Returns the type of the assignment.

        :returns: The assignment type.
        :rtype: Assignment.Type
        """
        if self._type is None:
            self._read_settings()
            assert self._type is not None, 'Error getting type from settings'
        return self._type

    def _read_settings(self) -> None:
        """Sets locally cached variables based on information available in the
        settings page.
        """
        # Fetch settings.
        res = self._client._get(endpoints.ASSIGNMENT_EDIT.substitute(
                                course_id=self._course.id,
                                assignment_id=self.id))
        html = lxml.html.fromstring(res.text)

        # Read assignment name.
        self._name = html.xpath('//input[@id="assignment_title"]/@value')[0]

        # Get type. Programming and online assignments are distinguished by the
        # data-controller attribute on the body of the settings page. The
        # remaining assignment types use the 'pdf_assignments' controller, so we
        # distinguish by seeing what hrefs are in the sidebar. Bubble sheets
        # have an href /bubble_sheet_answer_key. If not, exams have an href
        # /submission_batches. If not, it is a homework.
        controller = html.xpath('//body/@data-controller')[0]
        if controller == 'programming_assignments':
            self._type = Assignment.Type.PROGRAMMING
        elif controller == 'online_assignments':
            self._type = Assignment.Type.ONLINE
        elif controller == 'pdf_assignments':
            bubble_sheet_elems = html.xpath(f'//a[contains(@href,"/assignments/{self.id}/bubble_sheet_answer_key")]')
            if len(bubble_sheet_elems) > 0:
                self._type = Assignment.Type.BUBBLE_SHEET
            else:
                exam_elems = html.xpath(f'//a[contains(@href,"/assignments/{self.id}/submission_batches")]')
                if len(exam_elems) > 0:
                    self._type = Assignment.Type.EXAM
                else:
                    self._type = Assignment.Type.HOMEWORK
        else:
            raise GSInternalException('Unknown assignment controller type')
