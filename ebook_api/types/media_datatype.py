import re
from dataclasses import dataclass, field
from mimetypes import guess_extension, guess_type
from typing import Optional


@dataclass(eq=False, kw_only=True)
class MediaDatatype:
    content: bytes
    filename: Optional[str] = field(default=None)
    media_type: Optional[str] = field(default=None)
    extension: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        if self.media_type:
            self.__try_media_type(self.media_type)

        if self.extension:
            self.__try_extension(self.extension)

        if self.filename and re.search(self.__r_ext(), self.filename):
            self.__try_filename(self.filename)

    def __try_media_type(self, media_type: str) -> None:
        extension = guess_extension(media_type, strict=False)
        self.extension = extension

        if self.filename:
            self.filename = re.sub(self.__r_ext(), '', self.filename)
            self.filename += extension

    def __try_extension(self, extension: str) -> None:
        media_type, _ = guess_type('_' + extension, strict=False)
        self.media_type = media_type

        if self.filename:
            self.filename = re.sub(self.__r_ext(), '', self.filename)
            self.filename += extension

    def __try_filename(self, filename: str) -> None:
        media_type, _ = guess_type(filename, strict=False)
        extension = guess_extension(media_type, strict=False)

        self.media_type = media_type
        self.extension = extension

    def __r_ext(self) -> str:
        return r"\.[a-z]+$"


if __name__ == '__main__':
    from itertools import product

    filenames = ('filename.css', 'filename', None)
    media_types = ('text/css', 'image/png', None)
    extensions = ('.css', '.png', None)

    test_cases = tuple(product(filenames, media_types, extensions))

    for test_case in test_cases:
        filename, media_type, extension = test_case
        media = MediaDatatype(filename=filename,
                              media_type=media_type,
                              extension=extension)
        print('Filename:', filename)
        print('Media-Type:', media_type)
        print('Extension:', extension)
        print(media)
