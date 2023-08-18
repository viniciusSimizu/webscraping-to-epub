import logging
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from ebooklib import epub

from ebook_api.types.tag_datatype import MediaDatatype
from ebook_api.utils import EpubUtils

from .types.chapter_datatype import ChapterDatatype
from .types.epub_item_info import EpubItemInfo


@dataclass(eq=False, kw_only=True)
class Chapter:
    book: epub.EpubBook
    chpt_n: int
    imag_n: int = field(init=False, default=0)
    soup: BeautifulSoup = field(init=False, default_factory=BeautifulSoup)
    page: epub.EpubHtml = field(init=False, default_factory=epub.EpubHtml)

    def load(self, chapter: ChapterDatatype) -> epub.EpubHtml:
        page_info = EpubItemInfo(filename=EpubUtils.generate_filename(chapter.name) + '.xhtml',
                                 content=b'')
        self.page = EpubUtils.create_item(page_info, epub.EpubHtml)

        self.setup(chapter)

        self.load_styles(chapter)

        self.load_tags(chapter)

        return self.page

    def load_tags(self, chapter: ChapterDatatype) -> None:
        for tag in chapter.tags:
            elem = self.soup.new_tag(tag.name)

            match tag.name:
                case 'img':
                    self.load_media(tag.media)
                    elem['str'] = tag.media.filename
                case 'h3' | 'p':
                    elem.string = tag.text
                case _:
                    logging.warning(f"Non implemented Tag {tag.name!r}")
                    continue

            self.page.content += elem.encode()

    def load_media(self, media: MediaDatatype) -> None:
        if media.media_type.startswith('image'):
            media.filename = f"image_{self.chpt_n}_{self.imag_n}"
            self.imag_n += 1

        item_info = EpubItemInfo(filename=media.filename,
                                 media_type=media.media_type,
                                 content=media.content)
        item = EpubUtils.create_item(item_info, epub.EpubImage)

        self.book.add_item(item)

    def load_styles(self, chapter: ChapterDatatype) -> None:
        for style in chapter.css_styles:
            style_info = EpubItemInfo(filename=style.filename,
                                      content=style.content,
                                      media_type=style.media_type)
            self.page.add_item(EpubUtils.create_item(
                style_info, epub.EpubItem))

    def setup(self, chapter: ChapterDatatype) -> None:
        self.page.title = chapter.name

        properties = 'rendition:layout-pre-paginated rendition:orientation-auto rendition:spread-auto rendition:flow-paginated'
        self.page.properties.append(properties)
