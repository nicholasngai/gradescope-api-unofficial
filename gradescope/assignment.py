from __future__ import annotations

from dataclasses import dataclass, field
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

@dataclass(frozen=True)
class Assignment:
    _client: Client = field(repr=False, hash=False, compare=False)
    assignment_id: int
    name: str
