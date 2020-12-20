from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

@dataclass(frozen=True)
class Course:
    _client: Client = field(repr=False, hash=False, compare=False)
    course_id: int
    short_name: str
    name: str
    term: str
