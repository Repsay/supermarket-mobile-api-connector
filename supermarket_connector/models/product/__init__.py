from typing import Optional
from supermarket_connector.enums import ProductAvailabilityStatus, BonusType

from datetime import date

from abc import ABC, abstractclassmethod


class Product(ABC):
    # Info
    id: int
    name: Optional[str]
    unit_size: Optional[str]
    brand: Optional[str]
    description: Optional[str]
    nix18: bool
    nutriscore: Optional[str]

    # Price
    price_raw: Optional[float]
    price_current: Optional[float]
    unit_price_description: Optional[str]

    # Order info
    order_availability: Optional[ProductAvailabilityStatus]
    order_availability_description: Optional[str]
    available_online: bool

    # Bonus
    bonus: bool
    bonus_price: bool
    bonus_infinite: bool
    bonus_start_date: Optional[date]
    bonus_end_date: Optional[date]
    bonus_type: Optional[BonusType]
    bonus_mechanism: Optional[str]
    bonus_period_description: Optional[str]

    @abstractclassmethod
    def __init__(self) -> None:
        pass

    @abstractclassmethod
    def price(self):
        pass
