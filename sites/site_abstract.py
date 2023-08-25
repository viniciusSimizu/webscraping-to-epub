import asyncio
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
import shelve

from aiohttp import ClientSession

from ebook_api.types.volume_datatype import VolumeDatatype


@dataclass(eq=False, kw_only=True)
class Site(ABC):
    db: shelve.Shelf
    client: ClientSession
    queue: asyncio.Queue[VolumeDatatype | None]
    pool: ProcessPoolExecutor
    domains: tuple[str] = field(init=False)

    @abstractmethod
    async def producer_volume_data(self, url: str) -> None:
        """Produce VolumeDatatype data from given URL

        Returns:
            Tuple[VolumeDatatype]: Return structured VolumeDatatype
        """
