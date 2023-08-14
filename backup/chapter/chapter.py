"""Management of chapters"""

from aiohttp import ClientSession
from bs4 import Tag
from ebooklib import epub

from shared import css_chapter

from .types import ChapterConfig, ChapterData
from .utils import create_epub_image, generate_filename


class Chapter:
    def __init__(self, data: ChapterData, n: int, book: epub.EpubBook, session: ClientSession) -> None:
        self._chapter = epub.EpubHtml(content=b'')
        self.data = data
        self.chapter_number = n
        self._config = self._create_config(data)
        self._book = book
        self._session = session

    async def create(self) -> epub.EpubHtml:
        """Create book's chapter"""
        self._configure()
        self._set_style()

        image_count = 0
        for chapter_tag in self.data['tags']:
            if chapter_tag.name == 'img':
                await self.image_handler(chapter_tag, image_count)
                image_count += 1

            self._chapter.content += chapter_tag.encode()

        return self._chapter

    async def image_handler(self, img: Tag, n: int) -> None:
        epub_image = await create_epub_image(img['src'], self._session)
        epub_image.file_name = f"image_{self.chapter_number}_{n}"

        self._book.add_item(epub_image)
        img['src'] = epub_image.file_name

    def _configure(self) -> None:
        """Set chapter metadata"""
        self._chapter.title = self._config['title']

        self._chapter.file_name = f"{generate_filename(self._config['title'])}.xhtml"

        properties = 'rendition:layout-pre-paginated rendition:orientation-auto rendition:spread-auto rendition:flow-paginated'
        self._chapter.properties.append(properties)

    def _set_style(self) -> None:
        """Set chapter style"""
        self._chapter.add_item(css_chapter)

    def _create_config(self, data: ChapterData) -> ChapterConfig:
        return {
            'title': data['title']
        }
