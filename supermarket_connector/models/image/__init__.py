import dataclasses
from abc import ABC
from typing import Optional


@dataclasses.dataclass
class Image(ABC):
    url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
