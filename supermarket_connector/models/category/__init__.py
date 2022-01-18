from typing import Any, Optional

from abc import ABC
import dataclasses


@dataclasses.dataclass
class Category(ABC):
    id: int
    slug_name: Optional[str] = None
    name: Optional[str] = None
    nix18: bool = False

    images: list[Any] = dataclasses.field(default_factory=lambda: [])
    subs: list[Any] = dataclasses.field(default_factory=lambda: [])
