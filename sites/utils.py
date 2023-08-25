from pathlib import Path
from typing import Optional
from ebooklib import epub
from constants import EBOOK_FOLDER

from ebook_api.utils import EpubUtils


def create_style(css: bytes, uid: str) -> epub.EpubItem:
    return epub.EpubItem(uid=uid, media_type="text/css", content=css)


def already_exist(title: str, directory: Optional[str]) -> bool:
    path = Path(EBOOK_FOLDER)

    if directory:
        path /= directory

    filename = EpubUtils.generate_filename(title) + ".epub"
    path /= filename

    exist =  path.is_file()
    print(exist)
    return exist
