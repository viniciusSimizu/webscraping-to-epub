import asyncio
import logging
from dataclasses import dataclass
import re
from typing import List, Optional, Tuple
from pipe import map

from aiohttp import ClientResponseError, ClientSession
from bs4 import BeautifulSoup, Tag
from ebook_api.types.chapter_datatype import ChapterDatatype
from ebook_api.types.metadata_datatype import MetadataDatatype

from ebook_api.types.volume_datatype import VolumeDatatype

from ..site_abstract import Site


@dataclass
class RawChapterDatatype:
    url: str
    name: str


@dataclass
class RawVolumeDatatype:
    cover_url: str | None
    title: str
    series: str
    author: str
    chapters: Tuple[RawChapterDatatype]


@dataclass
class RawVolumeDatatypeAddons:
    series: str | None = None
    author: str | None = None


class Helper:
    @staticmethod
    def strip_string(text: str) -> str:
        return re.sub('[\xa0\n]+', '', text).strip()

    @staticmethod
    def is_heading(text: str) -> bool:
        return bool(re.search(r'^PARTE\W+\d+$', text, re.IGNORECASE))


@dataclass
class AnimeCenterBr(Site):
    domains = ('animecenterbr',)
    client: ClientSession
    queue: asyncio.Queue

    def __post_init__(self) -> None:
        self.toc_style = 'toc.css'
        self.chapter_style = 'chapter.css'

    async def extract_volume_data(self, url: str) -> Tuple[VolumeDatatype]:
        # try:
        #     async with self.client.get(url) as response:
        #         soup = BeautifulSoup(markup=await response.text('utf-8'), features='html.parser')
        # except ClientResponseError as error:
        #     logging.error(
        #         f"REQUEST ERROR - status: [{error.status}], message: \"{error.message}\" - trying to connect in {url}")
        #     raise ClientResponseError

        with open('test.html', 'r') as file:
            soup = BeautifulSoup(markup=file, features='html.parser')

        content: Tag = soup.select_one('.post-text-content')
        self.clean_soup(content)

        series = content.select_one(
            ':scope > h3:first-of-type').get_text(strip=True)

        page_info: RawVolumeDatatype = self.get_raw_volume(content)

        addons = RawVolumeDatatypeAddons(series=page_info.series)

        while raw_volume := self.get_raw_volume(content, addons):
            tasks = [self.extract_chapter_content(raw_chapter)
                     for raw_chapter in raw_volume.chapters]

            chapters: List[ChapterDatatype] = []

            for raw_chapter, tags_chapter in zip(raw_volume.chapters, await asyncio.gather(*tasks)):
                chapters.append(self.chapter_factory(raw_chapter=raw_chapter,
                                                     tags=tags_chapter))

            volume_data = self.volume_factory(raw_volume, tuple(chapters))

            print(volume_data)

            await self.queue.put(volume_data)
            break

    async def extract_chapter_content(self, raw_chapter: RawChapterDatatype) -> List[Tag]:
        async with self.client.get(raw_chapter.url) as response:
            soup = BeautifulSoup(await response.text('utf-8'))

        content: Tag = soup.select_one('.post-text-content')
        self.clean_soup(content)

        tags_to_format = content.select(':is(p, h1, h2, li)')
        for tag in tags_to_format:
            tag.string = Helper.strip_string(tag.get_text())

            if not tag.string:
                tag.extract()

        tags: List[Tag] = []

        for tag in content.select(':is(img, p, h1, h2, ul)'):
            match tag.name:
                case 'img':
                    img = soup.new_tag('img')
                    img['src'] = tag['src']
                    tags.append(img)
                case 'ul':
                    ul = soup.new_tag('ul')

                    for a in tag.select('a'):
                        a_ = soup.new_tag('a')
                        a_.string = a.get_text(strip=True)
                        a_['href'] = a['href']
                        ul.append(a_)
                    tags.append(ul)
                case _:
                    string = tag.get_text(strip=True)

                    t = soup.new_tag(
                        tag.name if not Helper.is_heading(string) else 'h3')
                    t.string = string
                    tags.append(t)

        return tags

    def get_raw_volume(self, soup: BeautifulSoup | Tag, addons: Optional[RawVolumeDatatypeAddons] = None) -> RawVolumeDatatype | None:
        img = soup.select_one(
            ":scope > img:not(:scope > :is(:has(a), :has(a) ~ *))")
        title = soup.select_one(":scope > :is(h3, span, strong, p)")
        chapters = soup.select_one(":scope > :is(ul, p):has(a)")

        if not img and not title and not chapters:
            return

        for tag in [img, title, chapters]:
            if tag:
                tag.extract()

        raw_chapters: List[RawChapterDatatype] = []

        for tag in chapters.select('a'):
            raw_chapters.append(RawChapterDatatype(name=tag.get_text(strip=True),
                                                   url=tag['href']))

        return RawVolumeDatatype(cover_url=img['src'] if img else None,
                                 title=title.get_text(strip=True),
                                 series=addons.series if addons else None,
                                 author=addons.author if addons else None,
                                 chapters=tuple(raw_chapters[:1]))

    def clean_soup(self, soup: BeautifulSoup) -> None:
        page_owner = soup.select(
            ':is(.awpa-title, .awpa-title ~ *, ul:last-of-type ~ *)') or []
        useless_tags = soup.select(':is(script, noscript, ins, br)') or []

        for tag in page_owner + useless_tags:
            tag.extract()

    def volume_factory(self, raw_volume: RawVolumeDatatype, chapters: Tuple[ChapterDatatype]) -> VolumeDatatype:
        metadata1 = MetadataDatatype(namespace=None,
                                     name='meta',
                                     value='',
                                     others={'name': 'calibre:series', 'content': raw_volume.series})

        return VolumeDatatype(title=raw_volume.title,
                              author=raw_volume.author,
                              cover_url=raw_volume.cover_url,
                              series=raw_volume.series,
                              chapters=chapters,
                              toc_css_styles=tuple([self.toc_style]),
                              chapter_css_styles=tuple([self.chapter_style]),
                              direction='rtl',
                              lang='pt-BR',
                              metadata=tuple([metadata1]))

    def chapter_factory(self, raw_chapter: RawChapterDatatype, tags: Tuple[Tag]) -> ChapterDatatype:
        properties = 'rendition:layout-pre-paginated rendition:orientation-auto rendition:spread-auto rendition:flow-paginated'

        return ChapterDatatype(name=raw_chapter.name,
                               tags=tags,
                               css_styles=tuple([self.chapter_style]),
                               properties=properties)
