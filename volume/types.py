from typing import Optional, Tuple, TypedDict

from chapter.types import ChapterData


class VolumeData(TypedDict):
    title: str
    cover_link: Optional[str]
    chapters_data: Tuple[ChapterData]
    order: int


class VolumeConfig(TypedDict):
    title: str
    author: Optional[str]
    series: Optional[str]
    cover_link: Optional[str]
    order: int
    lang: str
