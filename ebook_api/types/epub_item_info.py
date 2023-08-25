from dataclasses import dataclass, field

from .media_datatype import MediaDatatype


@dataclass(kw_only=True, eq=False)
class EpubItemInfo(MediaDatatype):
    manifest: bool = field(default=False)
