import asyncio

from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def producer(queue: asyncio.Queue) -> None:
    with open('links.txt') as file:
        while link := file.readline():
            await queue.put(link)
        await queue.put(None)


async def consumer(queue: asyncio.Queue, client: ClientSession) -> None:
    while True:
        link = await queue.get()

        if link is None:
            break

        async with client.get(link) as response:
            with open('test.html', 'wb') as file:
                soup = BeautifulSoup(await response.text('utf-8'), 'html.parser')
                file.write(soup.prettify('utf-8'))


async def main() -> None:
    async with ClientSession(headers={'accept': 'text/html'}) as client:
        queue = asyncio.Queue(1)

        async with asyncio.TaskGroup() as tg:
            prod = tg.create_task(producer(queue))
            cons = tg.create_task(consumer(queue, client))


asyncio.run(main())
