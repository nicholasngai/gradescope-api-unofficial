from __future__ import annotations

from dataclasses import dataclass, field
import enum
import json
from typing import Optional, TYPE_CHECKING

import lxml.html

from . import endpoints

if TYPE_CHECKING:
    from .client import Client
    from .course import Course

@dataclass
class Member:
    class Role(enum.Enum):
        INSTRUCTOR = enum.auto()
        TA = enum.auto()
        READER = enum.auto()
        STUDENT = enum.auto()

    id: int
    _client: Client = field(repr=False, hash=False, compare=False)
    _course: Course = field(repr=False, hash=False, compare=False)

    _name: Optional[str] = field(default=None, repr=False, hash=False,
                                compare=False)
    _email: Optional[str] = field(default=None, repr=False, hash=False,
                                 compare=False)
    _sid: Optional[int] = field(default=None, repr=False, hash=False,
                               compare=False)
    _role: Optional[Role] = field(default=None, repr=False, hash=False,
                                        compare=False)
    _canvas_connected: Optional[bool] = field(default=None, repr=False,
                                              hash=False, compare=False)

    def get_name(self, force: bool=False) -> str:
        """Returns the name of the member.

        :returns: The student's name.
        :rtype: str
        """
        if self._name is None or force:
            self._read_roster()
            assert self._name is not None, 'Failed to get name from roster'
        return self._name

    def get_email(self, force: bool=False) -> str:
        """Returns the email of the member.

        :returns: The student's email.
        :rtype: str
        """
        if self._email is None or force:
            self._read_roster()
            assert self._email is not None, 'Failed to get email from roster'
        return self._email

    def get_sid(self, force: bool=False) -> Optional[int]:
        """Returns the SID of the member, if set.

        :returns: The student's SID or None if the SID is not set.
        :rtype: Optional[int]
        """
        if self._sid is None or force:
            self._read_roster()
            assert self._sid is not None, 'Failed to get SID from roster'
        return self._sid if self._sid != -1 else None

    def get_role(self, force: bool=False) -> Role:
        """Returns the role of the member.

        :returns: The student's role.
        :rtype: Member.Role
        """
        if self._role is None or force:
            self._read_roster()
            assert self._role is not None, 'Failed to get role from roster'
        return self._role

    def get_canvas_connected(self, force: bool=False) -> bool:
        """Returns the whether the member is connected to a Canvas student.

        :returns: True if the student is connected to Canvas and False
        otherwise.
        :rtype: bool
        """
        if self._canvas_connected is None or force:
            self._read_roster()
            assert self._canvas_connected is not None, \
                    'Failed to get Canvas data from roster'
        return self._canvas_connected

    def _read_roster(self) -> None:
        """Sets locally cached variables based on information available in the
        course's roster page.
        """
        # Read roster table. All data can be found in the Edit button for each
        # member in the roster, so we will use this.
        res = self._client._get(endpoints.COURSE_MEMBERSHIP.substitute(
                course_id=self._course.id))
        html = lxml.html.fromstring(res.text)
        elems = html.xpath(f'//tr[contains(@class,"rosterRow") and .//@data-id="{self.id}"]//td')
        edit_elem = html.xpath(f'//tr[contains(@class,"rosterRow")]//*[@data-id="{self.id}"]')[0]
        cm_data = json.loads(edit_elem.xpath('@data-cm')[0])

        # Get name.
        self._name = cm_data['full_name']

        # Get email.
        self._email = edit_elem.xpath('@data-email')[0]

        # Get SID.
        self._sid = int(cm_data['sid']) if cm_data['sid'] != '' else -1

        # Get role.
        role_str = elems[2].xpath('//select//option[@selected="selected"]/text()')
        self._role = Member.Role[role_str.upper()]

        # Get Canvas link.
        active_canvas_elems = elems[4].xpath('//*[@data-sort="1"]')
        self._canvas_connected = len(active_canvas_elems) > 0
