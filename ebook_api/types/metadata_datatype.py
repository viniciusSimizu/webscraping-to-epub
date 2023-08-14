from dataclasses import dataclass
from typing import Any


@dataclass
class MetadataDatatype:
    namespace: Any
    name: Any
    value: Any
    others: Any | None = None
