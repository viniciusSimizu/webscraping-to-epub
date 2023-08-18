from dataclasses import dataclass, field
from typing import Literal, Optional

from .media_datatype import MediaDatatype


@dataclass(eq=False, kw_only=True)
class TagDatatype:
    name: Literal['img', 'h3', 'p']
    text: Optional[str] = field(default=None)
    media: Optional[MediaDatatype] = field(default=None)
