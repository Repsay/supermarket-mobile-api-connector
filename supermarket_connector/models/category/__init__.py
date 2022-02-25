from typing import Any, List, Optional, Union

from abc import ABC
import dataclasses


@dataclasses.dataclass
class Category(ABC):
    id: Union[int, str]
    slug_name: Optional[str] = None
    name: Optional[str] = None
    nix18: bool = False
    hasproducts: bool = True

    images: List[Any] = dataclasses.field(default_factory=lambda: [])
    subs: List[Any] = dataclasses.field(default_factory=lambda: [])
