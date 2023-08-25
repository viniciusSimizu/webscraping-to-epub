import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
import mimetypes
from os import cpu_count
from pathlib import Path
import shelve
from typing import Type

import tldextract
from aiohttp import ClientSession

from ebook_api.volume import Volume
from sites import sites
from sites.site_abstract import Site

logging.basicConfig(
    format="%(asctime)s [%(levelname)s]: %(message)s.",
    level=logging.DEBUG,
    filename=Path(".log"),
    filemode="w",
)

log = logging.getLogger(__name__)

mimetypes.add_type(type="image/webp", ext=".webp")


async def main():
    queue = asyncio.Queue(4)

    with shelve.open("pages") as db:
        async with ClientSession() as client:
            with ProcessPoolExecutor(max_workers=max(1, cpu_count() - 1)) as pool:
                with open("links.txt", "r") as file:
                    while link := file.readline():
                        domain = tldextract.extract(link).domain

                        site = find_site(domain)

                        if not site:
                            log.warning("The given url domain is not implemented")
                            continue

                        log.info(f"Processing following url: {link}")
                        async with asyncio.TaskGroup() as tg:
                            producer = tg.create_task(
                                site(
                                    client=client, db=db, queue=queue, pool=pool
                                ).producer_volume_data(url=link)
                            )
                            consumer = tg.create_task(
                                Volume.consume_volume_data(queue, pool)
                            )


def find_site(domain: str) -> Type[Site] | None:
    for site in sites:
        if domain in site.domains:
            return site


if __name__ == "__main__":
    log.info("Script started")
    try:
        asyncio.run(main())
    except KeyboardInterrupt as error:
        log.info("Script closed by user")
    finally:
        log.info("End of script")
