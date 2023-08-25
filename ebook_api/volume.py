import asyncio
import logging
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from ebooklib import ITEM_DOCUMENT, epub
from ebooklib.plugins.standard import SyntaxPlugin
from pipe import where

from constants import EBOOK_FOLDER
from ebook_api.utils import EpubUtils

from .chapter import Chapter
from .types.volume_datatype import VolumeDatatype

log = logging.getLogger(__name__)


@dataclass(eq=False, kw_only=True)
class Volume:
    data: VolumeDatatype

    book: epub.EpubBook = field(init=False, default_factory=epub.EpubBook)

    @staticmethod
    async def consume_volume_data(
        queue: asyncio.Queue[VolumeDatatype | None], pool: ProcessPoolExecutor
    ) -> None:
        status = True
        batch: list[VolumeDatatype] = []

        while status:
            data = await queue.get()

            if data is None:
                status = False
            else:
                batch.append(data)
                log.debug(f"Volume batched {data.title!r}")

            if (len(batch) >= pool._max_workers) or (not status and batch):
                tasks: list[Future] = []
                loop = asyncio.get_running_loop()

                for volume in [Volume(data=data) for data in batch]:
                    tasks.append(loop.run_in_executor(pool, Volume.load, volume))

                await asyncio.gather(*tasks)

    @staticmethod
    def load(cls: "Volume") -> None:
        log.info(f"Volume start saving: {cls.data.title!r}")

        cls.book_setup()

        chapters = [
            Chapter(book=cls.book, chpt_n=n, data=chapter).load()
            for n, chapter in enumerate(cls.data.all_chapters)
        ]
        for chapter in chapters:
            cls.book.add_item(chapter)
        log.debug(f"Volume {cls.data.title} Chapters loaded")

        cls.book_structure()
        cls.save()

    def save(self) -> None:
        """Save EPUB file"""
        opts = {"plugins": (SyntaxPlugin(),)}

        filename = self.data.filename

        if not filename:
            filename = EpubUtils.generate_filename(self.data.title)

        path = Path(EBOOK_FOLDER)

        if self.data.series:
            path /= self.data.series

        path.absolute().mkdir(parents=True, exist_ok=True)

        path /= filename + ".epub"

        epub.write_epub(name=path, book=self.book, options=opts)

        log.info(f"Volume end saving: {self.data.title!r}")

    def book_setup(self) -> None:
        self.book.set_title(self.data.title)
        self.book.set_direction(self.data.direction)
        self.book.set_language(self.data.lang)

        if self.data.series:
            self.book.add_metadata(
                None,
                "meta",
                "",
                {"name": "calibre:series", "content": self.data.series},
            )

        if self.data.cover:
            self.book.set_cover(
                file_name="cover" + self.data.cover.extension,
                content=self.data.cover.content,
            )

        if self.data.author:
            self.book.add_author(self.data.author)

        log.debug(f"Volume {self.data.title} setup finish")

    def book_structure(self) -> None:
        chapters: tuple[epub.EpubHtml] = tuple(
            self.book.get_items_of_type(ITEM_DOCUMENT)
            | where(lambda item: isinstance(item, epub.EpubHtml))
        )

        self.book.toc = chapters
        self.book.spine = ["nav", *chapters]

        if self.book.get_item_with_id("cover"):
            self.book.spine.insert(0, "cover")
        log.debug(f"Volume {self.data.title} book structured")
