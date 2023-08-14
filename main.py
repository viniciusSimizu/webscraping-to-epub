import asyncio

from aiohttp import ClientSession

from sites.customs.anime_center_br import AnimeCenterBr


async def main():
    queue = asyncio.Queue(1)
    async with ClientSession() as client:
        await AnimeCenterBr(client, queue).extract_volume_data('')


asyncio.run(main())
