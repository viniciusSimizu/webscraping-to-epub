import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from ebooklib import ITEM_DOCUMENT, epub
from ebooklib.plugins.standard import SyntaxPlugin
from pipe import where

from constants import EBOOK_FOLDER
from ebook_api.utils import EpubUtils

from .chapter import Chapter
from .types.volume_datatype import VolumeDatatype


@dataclass(eq=False, kw_only=True)
class Volume:
    pool: ProcessPoolExecutor

    book: epub.EpubBook = field(init=False, default_factory=epub.EpubBook)

    @staticmethod
    async def consume_volume_data(queue: asyncio.Queue[VolumeDatatype | None], pool: ProcessPoolExecutor) -> None:
        batch: list[VolumeDatatype] = []

        while status := True:
            data = await queue.get()

            if data is None:
                status = False
            else:
                batch.append(data)

            if (len(batch) >= pool._max_workers) or (not status and batch):
                pool.map(Volume(pool=pool).load, batch)

    def load(self, volume: VolumeDatatype) -> None:
        # Setup
        self.book_setup(volume)

        # Load Chapters
        for n, result in enumerate(volume.all_chapters):
            page = Chapter(book=self.book,
                           chpt_n=n).load(result)
            self.book.add_item(page)

        tasks: list[AsyncResult] = []
        for n, chapter in enumerate(volume.all_chapters):
            manager = Chapter(book=self.book,
                              chpt_n=n)
            tasks.append(self.pool.apply_async(manager.load, chapter))

        for result in tasks:
            self.book.add_item(result.get())

        # Create Structure
        self.book_structure()

        # Save
        self.save(volume)

    def save(self, volume: VolumeDatatype) -> None:
        """Save EPUB file"""
        opts = {'plugins': (SyntaxPlugin(),)}

        filename = volume.filename

        if not filename:
            filename = EpubUtils.generate_filename(volume.title)

        path = Path(EBOOK_FOLDER)

        if volume.series:
            path /= volume.series

        path /= filename + '.epub'

        epub.write_epub(path, opts)

    def book_setup(self, volume: VolumeDatatype) -> None:
        self.book.set_title(volume.title)
        self.book.set_direction(volume.direction)
        self.book.set_language(volume.lang)

        if volume.series:
            self.book.add_metadata(None, 'meta', '', {'name': 'calibre:series',
                                                      'content': volume.series})

        if volume.cover:
            self.book.set_cover(file_name='cover' + volume.cover.media.extension,
                                content=volume.cover.media.content)

        if volume.author:
            self.book.add_author(volume.author)

    def book_structure(self) -> None:
        chapters: tuple[epub.EpubHtml] = tuple(self.book.get_items_of_type(ITEM_DOCUMENT)
                                               | where(lambda item: isinstance(item, epub.EpubHtml)))

        self.book.toc = chapters
        self.book.spine = ['nav', *chapters]

        if self.book.get_item_with_id('cover'):
            self.book.spine.insert(0, 'cover')
