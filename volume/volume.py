"""Management of volumes"""

import asyncio
import mimetypes

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from ebooklib import ITEM_DOCUMENT, epub
from ebooklib.plugins.standard import SyntaxPlugin
from tqdm.asyncio import tqdm_asyncio

from chapter import Chapter
from constants import EBOOK_FOLDER
from shared import css_chapter, css_nav

from .types import VolumeConfig, VolumeData
from .utils import generate_volume_filename, generate_volume_title


class Volume:
    """Class that handle the volume flow"""

    def __init__(self, data: VolumeData, session: ClientSession) -> None:
        self._book = epub.EpubBook()
        self.data = data
        self._config = self._create_config(data)
        self._session = session

    async def start(self) -> None:
        """Main callable function"""
        self._configure_book()

        cover_task = asyncio.create_task(self._cover_book())

        await self._set_chapters()
        await cover_task

        self._set_structure()
        self.save()

    def save(self) -> None:
        """Download EPUB file"""
        opts = {'plugins': (SyntaxPlugin(),)}
        filename = generate_volume_filename(self._config['title'])

        epub.write_epub(f"{EBOOK_FOLDER}/{filename}.epub", self._book, opts)

    async def _set_chapters(self) -> None:
        """Set book chapters"""
        chapters_task = [asyncio.create_task(Chapter(data, n, self._book, self._session).create())
                         for n, data in enumerate(self.data['chapters_data'])]

        for chapter in await tqdm_asyncio.gather(*chapters_task,
                                                 desc=self.data['title'],
                                                 postfix=f"n: {self.data['order']}",
                                                 colour='GREEN'):
            self._book.add_item(chapter)

    async def _cover_book(self) -> None:
        """Set book cover"""
        if not self.data['cover_link']:
            return

        try:
            response = await self._session.get(self.data['cover_link'])
        except ClientConnectionError as err:
            print(f"Não foi possível baixar a imagem da capa - {err}")
            return

        extension = mimetypes.guess_extension(response.content_type, False)

        self._book.set_cover("cover" + extension, await response.read())

    def _set_styles(self) -> None:
        """Set book styles"""
        self._book.add_item(css_nav)
        self._book.add_item(css_chapter)

    def _set_navigators(self, book: epub.EpubBook) -> None:
        """Set book navigators"""
        nav = epub.EpubNav(title=self._config['title'])
        nav.add_item(css_nav)

        book.add_item(nav)
        book.add_item(epub.EpubNcx())

    def _set_structure(self) -> None:
        """Set book read order (spine)"""
        epub_chapters = [item for item in self._book.get_items_of_type(ITEM_DOCUMENT) if type(
            item) is epub.EpubHtml]

        self._book.toc = epub_chapters
        self._book.spine = ['nav', *epub_chapters]

        if self._book.get_item_with_id('cover'):
            self._book.spine.insert(0, 'cover')

    def _configure_book(self) -> None:
        """Set book metadata"""
        self._book.set_title(self._config['title'])
        self._book.add_author(self._config['author'])
        self._book.set_direction('rtl')
        self._book.set_language(self._config['lang'])
        self._book.add_metadata(None, 'meta', '', {'name': 'calibre:series',
                                                   'content': self._config['series']})

    def _create_config(self, data: VolumeData) -> VolumeConfig:
        return {
            'title': generate_volume_title(data['title'], 'Youkoso Jitsuryoku', data['order']),
            'cover_link': data['cover_link'],
            'order': data['order'],
            'lang': 'pt-br',
        }
