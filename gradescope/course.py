from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import List, Optional, TYPE_CHECKING

import lxml.html

from . import endpoints
from .assignment import Assignment

if TYPE_CHECKING:
    from .client import Client

@dataclass
class Course:
    _client: Client = field(repr=False, hash=False, compare=False)
    course_id: int
    short_name: str
    name: str
    term: str

    _is_instructor: Optional[bool] = field(default=None, repr=False,
                                           hash=False, compare=False)
    _description: Optional[str] = field(default=None, repr=False, hash=False,
                                        compare=False)

    @property
    def is_instructor(self) -> bool:
        """Whether the client is an instructor for this course. Controls the
        settings that the client has access to.

        :returns: True if the client is an instuctor and False otherwise.
        :rtype: bool
        """
        if self._is_instructor is None:
            # Try fetching the course editing endpoint to see if we can
            # successfully access it.
            res = self._client._get(endpoints.COURSE_ASSIGNMENTS.substitute(
                course_id=self.course_id))
            self._is_instructor = res.status_code == 200
        return self._is_instructor

    def get_description(self) -> str:
        """Returns the description for the course.

        :returns: The course description.
        :rtype: str
        """
        if self._description is None:
            self._read_dashboard()
            assert self._description is not None, \
                'Error getting description from dashboard'
        return self._description

    def get_assignments(self) -> List[Assignment]:
        """Fetches the list of assignments in the course. Raises an error if
        you are not an instructor of the course.

        :returns: A list of assignments.
        :rtype: list[Assignment]
        """
        if self.is_instructor:
            # We are an instructor.
            res = self._client._get(endpoints.COURSE_ASSIGNMENTS.substitute(
                course_id=self.course_id))
            html = lxml.html.fromstring(res.text)

            # Read courses from the HTML.
            assignments: List[Assignment] = []
            anchor_elems = html.xpath('//*[@id="assignments-instructor-table"]'
                                      '//tr'
                                      '//td[1]'
                                      '//a')
            for anchor_elem in anchor_elems:
                href = anchor_elem.xpath('@href')[0]
                name = anchor_elem.xpath('text()')[0]
                match = re.search('/assignments/(\d+)', href)
                assert match is not None, \
                        "Can't extract assignment ID from href"
                assignment_id = int(match.groups(1)[0])
                assignments.append(Assignment(self._client, assignment_id,
                                              name))
        elif not self._is_instructor:
            # We are a student. This is not supported yet.
            raise NotImplementedError('Student views are not implemented')

        return assignments

    def _read_dashboard(self) -> None:
        """Sets locally cached variables based on information available in the
        dashboard.
        """
        # Fetch description from the dashboard.
        res = self._client._get(endpoints.COURSE.substitute(
            course_id=self.course_id))
        html = lxml.html.fromstring(res.text)

        # Get description from the HTML.
        descriptions: List[str] = html.xpath('//*[contains(@class,"courseDashboard--panel-description")]//p/text()')
        self._description = '\n\n'.join(descriptions)
