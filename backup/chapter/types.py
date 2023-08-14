from typing import List, TypedDict

from bs4.element import Tag


class ChapterData(TypedDict):
    title: str
    tags: List[Tag]


class ChapterConfig(TypedDict):
    title: str
