import logging
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from ebooklib import epub

from ebook_api.types.tag_datatype import MediaDatatype
from ebook_api.utils import EpubUtils

from .types.chapter_datatype import ChapterDatatype
from .types.epub_item_info import EpubItemInfo

log = logging.getLogger(__name__)


@dataclass(eq=False, kw_only=True)
class Chapter:
    book: epub.EpubBook
    chpt_n: int
    data: ChapterDatatype
    imag_n: int = field(init=False, default=0)
    soup: BeautifulSoup = field(init=False, default_factory=BeautifulSoup)
    page: epub.EpubHtml = field(init=False, default_factory=epub.EpubHtml)

    def load(self) -> epub.EpubHtml:
        log.debug(f"Chapter start saving: {self.data.name!r}")
        page_info = EpubItemInfo(
            filename=EpubUtils.generate_filename(self.data.name) + ".xhtml",
            content=b"",
        )

        self.page = EpubUtils.create_item(page_info, epub.EpubHtml)

        self.setup()

        self.load_styles()

        self.load_tags()

        log.debug(f"Chapter end saving: {self.data.name!r}")

        return self.page

    def load_tags(self) -> None:
        for tag in self.data.tags:
            elem = self.soup.new_tag(tag.name)

            match tag.name:
                case "img":
                    self.load_media(tag.media)
                    elem["str"] = tag.media.filename
                case "h3" | "p":
                    elem.string = tag.text
                case _:
                    logging.warning(f"Non implemented Tag {tag.name!r}")
                    continue

            self.page.content += elem.encode()
        log.debug(f"Chapter {self.data.name!r} content loaded")

    def load_media(self, media: MediaDatatype) -> None:
        if media.media_type.startswith("image"):
            media.filename = f"image_{self.chpt_n}_{self.imag_n}"
            self.imag_n += 1

        item_info = EpubItemInfo(
            filename=media.filename, media_type=media.media_type, content=media.content
        )
        item = EpubUtils.create_item(item_info, epub.EpubImage)

        self.book.add_item(item)

    def load_styles(self) -> None:
        for style in self.data.css_styles:
            style_info = EpubItemInfo(
                filename=style.filename,
                content=style.content,
                media_type=style.media_type,
            )
            self.page.add_item(EpubUtils.create_item(style_info, epub.EpubItem))
        log.debug(f"Chapter {self.data.name!r} styles loaded")

    def setup(self) -> None:
        self.page.title = self.data.name

        properties = "rendition:layout-pre-paginated rendition:orientation-auto rendition:spread-auto rendition:flow-paginated"
        self.page.properties.append(properties)

        log.debug(f"Chapter {self.data.name!r} setup finished")
