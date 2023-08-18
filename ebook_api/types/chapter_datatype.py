from dataclasses import dataclass

from .media_datatype import MediaDatatype
from .tag_datatype import TagDatatype


@dataclass(frozen=True, kw_only=True, eq=False)
class ChapterDatatype:
    name: str
    tags: tuple[TagDatatype]
    css_styles: tuple[MediaDatatype]
