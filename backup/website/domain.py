import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from chapter import chapter_data_factory
from chapter.types import ChapterData
from utils import strip_string
from volume import VolumeData, volume_data_factory


class Site(ABC):
    domain: str
    headers: Optional[Dict[str, str]]

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    @abstractmethod
    async def extract_volumes(self, link: str) -> List[VolumeData]:
        """Transform website tags into a structured VolumeData"""


class AnimeCenterBr(Site):
    domain = 'animecenterbr'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8,pt;q=0.7',
    }

    async def extract_volumes(self, link: str) -> List[VolumeData]:
        print('Extracting data...')

        response = await self._session.get(url=link, headers=self.headers)

        soup = BeautifulSoup(await response.text(), 'html.parser')

        tags_to_remove = soup.select(
            '.post-text-content :is(.awpa-title, .awpa-title ~ *, ul:last-of-type ~ *)')
        for tag in tags_to_remove:
            tag.extract()

        tags = soup.select(
            '.post-text-content :is(ul ~ :is(img, :is(span, strong, p:not(:has(+ p)))), ul ~ * a)')

        return await self.create_volume_data(tags)

    async def create_volume_data(self, tags: List[Tag]) -> List[VolumeData]:
        """ Separate page tags and structure them """
        volumes_data: List[VolumeData] = []

        link_reached = False
        order = 1

        volume_tags: List[Tag] = []

        last_item = tags[-1]
        for tag in tags:
            is_last = tag == last_item

            if is_last:
                volume_tags.append(tag)

            if (link_reached and tag.name != 'a') or is_last:
                volume_image_tag, volume_title_tag, *chapter_link_tags = volume_tags

                task_chapters: List[asyncio.Task] = []

                async with asyncio.TaskGroup() as tg:
                    for chapter_tag in chapter_link_tags:
                        task_chapters.append(tg.create_task(
                            self.create_chapter_data(chapter_tag)))

                volume_data: VolumeData = (volume_data_factory(volume_title_tag.text, volume_image_tag['src'], [
                    task.result() for task in task_chapters if not task.cancelled()], order))

                volumes_data.append(volume_data)
                order += 1
                volume_tags.clear()

            if tag.name == 'a':
                link_reached = True
            else:
                link_reached = False

            volume_tags.append(tag)

        return volumes_data

    async def create_chapter_data(self, chapter_tag: Tag) -> ChapterData:
        tags = await self.extract_chapter_tags(chapter_tag['href'])

        return chapter_data_factory(title=chapter_tag.text, tags=tags)

    async def extract_chapter_tags(self, chapter_link: str) -> List[Tag]:
        response = await self._session.get(chapter_link, headers=self.headers)

        soup = BeautifulSoup(await response.read(), 'html.parser')

        tags_to_remove = soup.select(
            '.post-text-content :is(script, noscript, ins, .awpa-title, .awpa-title ~ *)')
        for tag in tags_to_remove:
            tag.extract()

        tags_to_format = soup.select('.post-text-content :is(p, h1, h2, li)')
        for tag in tags_to_format:
            tag.string = strip_string(tag.text)

            if not tag.string:
                tag.extract()

        return soup.select('.post-text-content :is(img, p, h1, h2, ul)')
