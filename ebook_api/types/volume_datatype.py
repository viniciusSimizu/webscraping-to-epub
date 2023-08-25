"""The Volume datatype"""

from dataclasses import dataclass, field
from typing import Literal, Optional, Tuple

from .chapter_datatype import ChapterDatatype
from .media_datatype import MediaDatatype
from .metadata_datatype import MetadataDatatype


@dataclass
class VolumeDatatype:
    title: str
    all_chapters: Tuple[ChapterDatatype]
    toc_css_styles: Tuple[MediaDatatype]
    chapter_css_styles: Tuple[MediaDatatype]
    metadata: Tuple[MetadataDatatype]

    cover: Optional[MediaDatatype] = field(default=None)
    author: Optional[str] = field(default=None)
    series: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    lang: str = field(default="pt-BR")
    direction: Literal["ltr", "rtl"] = field(default="ltr")
