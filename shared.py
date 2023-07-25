"""Variable shared between modules"""

import pathlib

from ebooklib import epub

from constants import CSS_FOLDER

css_nav = epub.EpubItem(uid='style_nav',
                        file_name=f"{CSS_FOLDER}/nav.css",
                        media_type='text/css',
                        content=pathlib.Path(f"{CSS_FOLDER}/nav.css").read_bytes())

css_chapter = epub.EpubItem(uid='style_chapter',
                            file_name=f"{CSS_FOLDER}/chapter.css",
                            media_type='text/css',
                            content=pathlib.Path(f"{CSS_FOLDER}/chapter.css").read_bytes())
