"""Application Entry-Point"""
import asyncio

import tldextract
from aiohttp import ClientSession

from utils import strip_string
from volume import Volume
from website.domain_manager import domain_map


async def async_main():
    """Run program"""
    async with ClientSession() as session:
        with open('links.txt', 'r') as file:
            while link := strip_string(file.readline()):
                domain = tldextract.extract(link).domain
                site = domain_map[domain](session)

                volumes_data = await site.extract_volumes(link)

                await asyncio.gather(*[Volume(volume_data, session).start() for volume_data in volumes_data])


asyncio.run(async_main())
