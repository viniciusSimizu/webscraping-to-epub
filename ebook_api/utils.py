from typing import TypeVar

from ebooklib import epub

from ebook_api.types.epub_item_info import EpubItemInfo
from ebook_api.types.media_datatype import MediaDatatype

T = TypeVar("T", bound=epub.EpubItem)


class EpubUtils:
    @staticmethod
    def create_item(info: EpubItemInfo, item: type[T] = type[epub.EpubItem]) -> T:
        if info.manifest:
            return item(
                content=info.content,
                file_name=info.filename,
                media_type=info.media_type,
                manifest=info.manifest,
            )

        return item(
            content=info.content, file_name=info.filename, media_type=info.media_type
        )

    @staticmethod
    def generate_filename(title: str) -> str:
        """Generate filename"""
        import re

        from unidecode import unidecode

        return (
            re.sub(r"[^A-Z\d]+", " ", unidecode(title), flags=re.IGNORECASE)
            .title()
            .strip()
        )
