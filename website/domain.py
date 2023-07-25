from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from aiohttp import ClientSession
from volume import VolumeData


class Site(ABC):
    domain: str
    headers: Optional[Dict[str, str]]

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    @abstractmethod
    async def extract_volumes(self, link: str) -> List[VolumeData]:
        """Transform website tags into a structured VolumeData"""
