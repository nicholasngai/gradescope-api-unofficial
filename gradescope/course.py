from __future__ import annotations

from dataclasses import dataclass, field
import functools
import re
from typing import List, Optional, TYPE_CHECKING

import lxml.html

from . import endpoints
from .assignment import Assignment
from .error import GSNotAuthorizedException
from .term import Term

if TYPE_CHECKING:
    from .client import Client

# TODO I have no idea how to statically type this.
def _require_instructor(func):
    @functools.wraps(func)
    def wrapper(self: Course, *args, **kwargs):
        if not self.is_instructor:
            raise GSNotAuthorizedException(
                    'Must be instructor to execute this function')
        return func(self, *args, **kwargs)
    return wrapper

@dataclass
class Course:
    _client: Client = field(repr=False, hash=False, compare=False)
    id: int

    _is_instructor: Optional[bool] = field(default=None, repr=False,
                                           hash=False, compare=False)
    _short_name: Optional[str] = field(default=None, repr=False, hash=False,
                                       compare=False)
    _name: Optional[str] = field(default=None, repr=False, hash=False,
                                 compare=False)
    _term: Optional[Term] = field(default=None, repr=False, hash=False,
                                  compare=False)
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
                course_id=self.id))
            self._is_instructor = res.status_code == 200
        return self._is_instructor

    def get_short_name(self, *, force_update: bool=False) -> str:
        """Returns the course's short name, typically in the form of 'DEPT
        XXX'.

        :param force_update: If True, force an update instead of using the
        locally cached data.
        :type force_update: bool
        :returns: The course short name.
        :rtype: str
        """
        if self._short_name is None or force_update:
            self._read_dashboard()
            assert self._short_name is not None, \
                    'Error getting short name from dashboard'
        return self._short_name

    @_require_instructor
    def set_short_name(self, new_short_name: str) -> None:
        """Update the course's short name, typically in the form of 'DEPT XXX'.

        :param new_short_name: The new short name.
        :type new_short_name: str
        """
        res = self._client._post(
                endpoints.COURSE.substitute(course_id=self.id),
                data={
                    '_method': 'patch',
                    'course[shortname]': new_short_name,
                })
        self._short_name = None

    def get_name(self, *, force_update: bool=False) -> str:
        """Returns the course's full name.

        :param force_update: If True, force an update instead of using the
        locally cached data.
        :type force_update: bool
        :returns: The course full name.
        :rtype: str
        """
        if self._name is None or force_update:
            self._read_dashboard()
            assert self._name is not None, \
                    'Error getting name from dashboard'
        return self._name

    @_require_instructor
    def set_name(self, new_name: str) -> None:
        """Update the course's full name.

        :param new_name: The new short name.
        :type new_name: str
        """
        res = self._client._post(
                endpoints.COURSE.substitute(course_id=self.id),
                data={
                    '_method': 'patch',
                    'course[name]': new_name,
                })
        self._name = None

    def get_term(self, *, force_update: bool=False) -> Term:
        """Returns the course's term.

        :param force_update: If True, force an update instead of using the
        locally cached data.
        :type force_update: bool
        :returns: The course term.
        :rtype: Term
        """
        if self._term is None or force_update:
            self._read_dashboard()
            assert self._term is not None, \
                    'Error getting term from dashboard'
        return self._term

    @_require_instructor
    def set_term(self, new_term: Term) -> None:
        """Update the course's term.

        :param new_term: The new term.
        :type new_term: Term
        """
        res = self._client._post(
                endpoints.COURSE.substitute(course_id=self.id),
                data={
                    '_method': 'patch',
                    'course[term]': new_term.season.name.capitalize(),
                    'course[year]': str(new_term.year)
                })
        self._term = None

    def get_description(self, *, force_update: bool=False) -> str:
        """Returns the description for the course.

        :param force_update: If True, force an update instead of using the
        locally cached data.
        :type force_update: bool
        :returns: The course description.
        :rtype: str
        """
        if self._description is None or force_update:
            self._read_dashboard()
            assert self._description is not None, \
                    'Error getting description from dashboard'
        return self._description

    @_require_instructor
    def set_description(self, new_description: str) -> None:
        """Update the course's description.

        :param new_description: The new description.
        :type new_description: str
        """
        res = self._client._post(
                endpoints.COURSE.substitute(course_id=self.id),
                data={
                    '_method': 'patch',
                    'course[description]': new_description,
                })
        self._description = None

    def get_assignments(self) -> List[Assignment]:
        """Returns the list of assignments in the course. Raises an error if you
        are not an instructor of the course.

        :returns: A list of assignments.
        :rtype: list[Assignment]
        """
        if self.is_instructor:
            # We are an instructor.
            res = self._client._get(endpoints.COURSE_ASSIGNMENTS.substitute(
                course_id=self.id))
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
                assignments.append(Assignment(_client=self._client,
                                              _course=self, id=assignment_id,
                                              _name=name))
        elif not self._is_instructor:
            # We are a student. This is not supported yet.
            raise NotImplementedError('Student views are not implemented')

        return assignments

    def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Returns the assignment with the given ID, if it exists.

        :param assignment_id: The ID of the assignment.
        :type assignment_id: int
        :returns: The assignment if it exists or None otherwise.
        :rtype: Optional[Assignment]
        """
        assignments = self.get_assignments()
        for assignment in assignments:
            if assignment.id == assignment_id:
                return assignment
        return None

    def _read_dashboard(self) -> None:
        """Sets locally cached variables based on information available in the
        dashboard.
        """
        # Fetch dashboard.
        res = self._client._get(endpoints.COURSE.substitute(course_id=self.id))
        html = lxml.html.fromstring(res.text)

        # Read short name.
        self._short_name = html.xpath('//*[contains(@class,"sidebar--title")]//text()')[0]

        # Read name.
        self._name = html.xpath('//*[contains(@class,"sidebar--subtitle")]//text()')[0]

        # Read term.
        self._term = Term.parse(html.xpath('//*[contains(@class,"courseHeader--term")]//text()')[0])

        # Read description.
        descriptions = html.xpath('//*[contains(@class,"courseDashboard--panel-description")]'
                                  '//p[not(contains(@class,"u-placeholderText"))]'
                                  '/text()')
        self._description = '\n\n'.join(descriptions)
