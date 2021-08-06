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

    def fetch_assignments(self) -> List[Assignment]:
        """Fetches the list of assignments in the course. Raises an error if
        you are not an instructor of the course..

        :returns: A list of assignments.
        :rtype: list[Assignment]
        """
        if self._is_instructor is None or self._is_instructor:
            # Either we are instructor or we don't know, so try making a
            # request to the assignments endpoint.
            res = self._client._get(endpoints.COURSE_ASSIGNMENTS.substitute(
                course_id=self.course_id))
            if self._is_instructor is None:
                if res.status_code != 200:
                    # We learned that we are not the instructor. Set the flag
                    # and try again.
                    self._is_instructor = False
                    return self.fetch_assignments()
                else:
                    # Else, set the flag, and we can safely continue to the
                    # main instructor handler.
                    self._is_instructor = True

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
