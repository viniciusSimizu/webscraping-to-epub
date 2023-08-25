import asyncio
import logging
import re
import shelve
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from constants import CSS_FOLDER
from ebook_api.types.chapter_datatype import ChapterDatatype
from ebook_api.types.epub_item_info import EpubItemInfo
from ebook_api.types.media_datatype import MediaDatatype
from ebook_api.types.metadata_datatype import MetadataDatatype
from ebook_api.types.tag_datatype import TagDatatype
from ebook_api.types.volume_datatype import VolumeDatatype
from sites.utils import already_exist
from utils import uri_path

from ..site_abstract import Site

log = logging.getLogger(__name__)


@dataclass(frozen=True, eq=False, kw_only=True)
class RawChapterDatatype:
    url: str
    name: str


@dataclass(frozen=True, eq=False, kw_only=True)
class RawVolumeDatatype:
    cover_url: Optional[str]
    title: str
    series: str
    author: str
    chapters: tuple[RawChapterDatatype]


@dataclass(frozen=True, eq=False, kw_only=True)
class RawVolumeDatatypeAddons:
    series: Optional[str] = field(default=None)
    author: str = field(init=False, default="Shōgo Kinugasa")


class Helper:
    @staticmethod
    def strip_string(text: str) -> str:
        return re.sub("[\xa0\n]+", "", text).strip()

    @staticmethod
    def is_heading(text: str) -> bool:
        return bool(re.search(r"^PARTE\W+\d+$", text, re.IGNORECASE))


@dataclass
class AnimeCenterBr(Site):
    db: shelve.Shelf
    client: ClientSession
    queue: asyncio.Queue[VolumeDatatype | None]
    pool: ProcessPoolExecutor

    domains: tuple[str] = field(init=False, default=("animecenterbr",))
    toc_style: str = field(init=False, default="toc.css")
    chapter_style: str = field(init=False, default="chapter.css")

    def __post_init__(self) -> None:
        self.toc_style: MediaDatatype = MediaDatatype(
            filename=self.toc_style,
            content=(Path(CSS_FOLDER) / self.toc_style).read_bytes(),
            extension=".css",
            media_type="text/css",
        )
        self.chapter_style: MediaDatatype = MediaDatatype(
            filename=self.chapter_style,
            content=(Path(CSS_FOLDER) / self.chapter_style).read_bytes(),
            extension=".css",
            media_type="text/css",
        )

    async def producer_volume_data(self, url: str) -> None:
        log.debug("Producer is running")

        soup = BeautifulSoup(markup=self.db.get(uri_path(url)), features="html.parser")
        log.info("Source page loaded")

        soup: Tag = soup.select_one(".post-text-content")
        self.clean_soup(soup)

        series = soup.select_one(":scope > h3:first-of-type").get_text(strip=True)

        # Remove introduction
        self.get_raw_volume(soup)

        addons = RawVolumeDatatypeAddons(series=series)

        while raw_volume := self.get_raw_volume(soup, addons):
            chapters: list[ChapterDatatype] = []

            for raw_chapter in raw_volume.chapters:
                chapter_soup = self.extract_page(raw_chapter.url)
                tags = self.extract_chapter_tags(chapter_soup)

                chapters.append(
                    await self.chapter_factory(
                        raw_chapter=raw_chapter, tags=tuple(tags)
                    )
                )
                log.info(f"Chapter loaded {raw_chapter.name!r}")

            cover = None
            if raw_volume.cover_url:
                cover = await self.extract_media(raw_volume.cover_url)

            volume_data = self.volume_factory(raw_volume, tuple(chapters), cover)
            log.info(f"Volume loaded {raw_volume.title!r}")

            await self.queue.put(volume_data)

        await self.queue.put(None)
        log.debug("Producer has closed")

    def extract_chapter_tags(self, soup: BeautifulSoup) -> tuple[TagDatatype]:
        content: Tag = soup.select_one(".post-text-content")

        tags_to_format = content.select(":is(p, h1, h2, li)")
        for tag in tags_to_format:
            tag.string = Helper.strip_string(tag.get_text(strip=True))

            if not tag.string:
                tag.extract()

        tags: list[TagDatatype] = []

        for tag in content.select(":is(img, p, h1, h2, h3, ul)"):
            elem: Tag | None = None

            match tag.name:
                case "img":
                    elem = soup.new_tag("img")
                    elem["src"] = tag["src"]
                case "ul":
                    elem = soup.new_tag("ul")

                    for a in tag.select("a"):
                        a_ = soup.new_tag("a")
                        a_.string = a.get_text(strip=True)
                        a_["href"] = a["href"]
                        elem.append(a_)
                case _:
                    string = tag.get_text(strip=True)

                    if tag.name in ["h1", "h2", "h3"] or Helper.is_heading(string):
                        elem = soup.new_tag("h3")
                    else:
                        elem = soup.new_tag("p")

                    elem.string = string

            tags.append(elem)

        return tuple(tags)

    def extract_page(self, url: str) -> BeautifulSoup:
        soup = BeautifulSoup(markup=self.db.get(uri_path(url)), features="html.parser")

        self.clean_soup(soup)
        return soup

    async def extract_media(self, url: str) -> MediaDatatype:
        async with self.client.get(url) as response:
            return MediaDatatype(
                filename=response.url.name,
                content=await response.read(),
                media_type=response.content_type,
            )

    def get_raw_volume(
        self,
        soup: BeautifulSoup | Tag,
        addons: Optional[RawVolumeDatatypeAddons] = None,
    ) -> RawVolumeDatatype | None:
        img = soup.select_one(":scope > img:not(:scope > :is(:has(a), :has(a) ~ *))")
        title = soup.select_one(":scope > :is(h3, span, strong, p)")
        chapters = soup.select_one(":scope > :is(ul, p):has(a)")

        if not img and not title and not chapters:
            return

        for tag in [img, title, chapters]:
            if not tag:
                continue

            tag.extract()

        if addons and already_exist(title.get_text(strip=True), addons.series):
            return self.get_raw_volume(soup, addons)

        raw_chapters: list[RawChapterDatatype] = []

        for tag in chapters.select("a"):
            raw_chapters.append(
                RawChapterDatatype(name=tag.get_text(strip=True), url=tag["href"])
            )

        return RawVolumeDatatype(
            cover_url=img["src"] if img else None,
            title=title.get_text(strip=True),
            series=addons.series if addons else None,
            author=addons.author if addons else None,
            chapters=tuple(raw_chapters),
        )

    def clean_soup(self, soup: BeautifulSoup) -> None:
        page_owner = (
            soup.select(":is(.awpa-title, .awpa-title ~ *, ul:last-of-type ~ *)") or []
        )
        useless_tags = soup.select(":is(script, noscript, ins, br)") or []

        for tag in page_owner + useless_tags:
            tag.extract()

    def volume_factory(
        self,
        raw_volume: RawVolumeDatatype,
        chapters: tuple[ChapterDatatype],
        cover: Optional[MediaDatatype],
    ) -> VolumeDatatype:
        metadata_series = MetadataDatatype(
            namespace=None,
            name="meta",
            value="",
            others={"name": "calibre:series", "content": raw_volume.series},
        )

        return VolumeDatatype(
            title=raw_volume.title,
            author=raw_volume.author,
            cover=cover,
            series=raw_volume.series,
            all_chapters=chapters,
            toc_css_styles=tuple([self.toc_style]),
            chapter_css_styles=tuple([self.chapter_style]),
            direction="rtl",
            lang="pt-BR",
            metadata=tuple([metadata_series]),
        )

    async def chapter_factory(
        self, raw_chapter: RawChapterDatatype, tags: tuple[Tag]
    ) -> ChapterDatatype:
        return ChapterDatatype(
            name=raw_chapter.name,
            tags=tuple(await asyncio.gather(*map(self.tag_factory, tags))),
            css_styles=tuple([self.chapter_style]),
        )

    async def tag_factory(self, tag: Tag) -> TagDatatype:
        if tag.name == "img":
            return TagDatatype(
                name=tag.name, media=await self.extract_media(tag["src"])
            )

        return TagDatatype(name=tag.name, text=tag.get_text(strip=True))
