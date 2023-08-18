from typing import TypeVar

from ebooklib import epub

from ebook_api.types.epub_item_info import EpubItemInfo

T = TypeVar('T', bound=epub.EpubItem)


class EpubUtils:
    @staticmethod
    def create_item(info: EpubItemInfo, item: type[T] = type[epub.EpubItem]) -> T:
        return item(content=info.media.content,
                    file_name=info.media.filename,
                    media_type=info.media.media_type,
                    manifest=info.manifest)

    @staticmethod
    def generate_filename(title: str) -> str:
        """ Generate filename """
        import re

        import unidecode

        return re.sub(r'[^A-Z\d]+', ' ', unidecode(title), flags=re.IGNORECASE).title().strip()
