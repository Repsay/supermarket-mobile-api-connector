from __future__ import annotations

from typing import Optional

from abc import ABC, abstractclassmethod


class Category(ABC):
    id: int
    slug_name: Optional[str]
    name: Optional[str]
    nix18: bool

    @abstractclassmethod
    def __init__(self) -> None:
        pass
