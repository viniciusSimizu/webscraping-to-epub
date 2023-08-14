import re
from typing import List

from aiohttp import ClientSession
from bs4 import Tag
from ebooklib import epub
from unidecode import unidecode

from utils import strip_string

from .types import ChapterData


def chapter_data_factory(title: str, tags: List[Tag]) -> ChapterData:
    """Create Chapter Data"""
    return {'title': strip_string(title), 'tags': tags}


def generate_filename(chapter_title: str) -> str:
    return re.sub(r"[^\w\s]+", '', unidecode(chapter_title.strip())).lower()


async def create_epub_image(image_link: str, session: ClientSession) -> epub.EpubImage:
    response = await session.get(image_link)

    epub_image = epub.EpubImage(media_type=response.content_type,
                                content=await response.read())

    return epub_image
