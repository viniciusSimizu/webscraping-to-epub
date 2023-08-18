from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True, kw_only=True, eq=False)
class MetadataDatatype:
    namespace: any
    name: any
    value: any
    others: Optional[any] = field(default=None)
