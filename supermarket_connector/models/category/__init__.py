from typing import Any, List, Optional

from abc import ABC
import dataclasses


@dataclasses.dataclass
class Category(ABC):
    id: int
    slug_name: Optional[str] = None
    name: Optional[str] = None
    nix18: bool = False

    images: List[Any] = dataclasses.field(default_factory=lambda: [])
    subs: List[Any] = dataclasses.field(default_factory=lambda: [])
