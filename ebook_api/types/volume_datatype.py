"""The Volume datatype"""

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

from .chapter_datatype import ChapterDatatype
from .metadata_datatype import MetadataDatatype
from ebooklib import epub


@dataclass
class VolumeDatatype:
    title: str
    author: str
    series: str
    lang: str
    direction: Literal['ltr', 'rtl']
    cover_url: Optional[str]
    chapters: Tuple[ChapterDatatype]
    toc_css_styles: Tuple[epub.EpubItem]
    chapter_css_styles: Tuple[epub.EpubItem]
    metadata: Tuple[MetadataDatatype]
