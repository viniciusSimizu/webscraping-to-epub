import asyncio
from abc import ABC, abstractmethod
from typing import Any, Tuple

from aiohttp import ClientSession

from ebook_api.types.volume_datatype import VolumeDatatype


class Site(ABC):
    domains: Tuple[str]
    client: ClientSession
    queue: asyncio.Queue

    @abstractmethod
    async def extract_volume_data(self, *args: Any, **kwargs: Any) -> Tuple[VolumeDatatype]:
        """Extract data from given URL

        Returns:
            Tuple[VolumeDatatype]: Return structured VolumeDatatype
        """
