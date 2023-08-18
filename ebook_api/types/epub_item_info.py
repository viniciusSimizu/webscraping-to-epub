from dataclasses import dataclass, field

from .media_datatype import MediaDatatype


@dataclass(frozen=True, kw_only=True, eq=False)
class EpubItemInfo:
    media: MediaDatatype
    manifest: bool = field(default=False)
