"""The Chapter datatype"""

from dataclasses import dataclass
from typing import Tuple

from bs4 import Tag


@dataclass
class ChapterDatatype:
    name: str
    tags: Tuple[Tag]
    css_styles: Tuple[str]
    properties: Tuple[str]
