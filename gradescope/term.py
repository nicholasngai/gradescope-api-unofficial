from __future__ import annotations

from dataclasses import dataclass, field
import enum
import re

@dataclass
class Term:
    class Season(enum.Enum):
        SPRING = 1
        SUMMER = 2
        FALL = 3
        WINTER = 4
    season: Term.Season
    year: int

    _PARSE_RE = re.compile('(SPRING|SUMMER|FALL|WINTER)\s*(\d+)')

    @staticmethod
    def parse(s: str) -> Term:
        """Parses the string into a term. Parsing is done as liberally as
        possible, ignoring capitalization and spacing between the season and the
        year.

        :param s: The string to parse.
        :type s: str
        :returns: The parsed term.
        :rtype: Term
        """
        s = s.upper()
        match = Term._PARSE_RE.fullmatch(s)
        if not match:
            raise ValueError(f'String does not represent a valid term: {s}')
        season = Term.Season[match.group(1)]
        year = int(match.group(2))
        return Term(season, year)
