from abc import ABC, abstractclassmethod
from typing import Optional


class Image(ABC):
    height: Optional[int]
    width: Optional[int]
    url: Optional[str]

    @abstractclassmethod
    def __init__(self) -> None:
        pass
