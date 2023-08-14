from ebooklib import epub


def create_style(css: bytes, uid: str) -> epub.EpubItem:
    return epub.EpubItem(uid=uid,
                         media_type='text/css',
                         content=css)
