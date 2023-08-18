"""The Volume datatype"""

from dataclasses import dataclass, field
from typing import Literal, Optional, Tuple

from ebook_api.types.epub_item_info import EpubItemInfo

from .chapter_datatype import ChapterDatatype
from .metadata_datatype import MetadataDatatype
from .media_datatype import MediaDatatype


@dataclass
class VolumeDatatype:
    title: str
    all_chapters: Tuple[ChapterDatatype]
    toc_css_styles: Tuple[MediaDatatype]
    chapter_css_styles: Tuple[MediaDatatype]
    metadata: Tuple[MetadataDatatype]

    cover: Optional[EpubItemInfo] = field(default=None)
    author: Optional[str] = field(default=None)
    series: Optional[str] = field(default=None)
    filename: Optional[str] = field(default=None)
    lang: str = field(default='pt-BR')
    direction: Literal['ltr', 'rtl'] = field(default='ltr')
