from enum import Enum, auto


class ProductSort(Enum):
    RELEVANCE = "RELEVANCE"
    PRICEHIGHLOW = "PRICEHIGHLOW"
    PRICELOWHIGH = "PRICELOWHIGH"
    TAXONOMY = "TAXONOMY"
    PURCHASE_FREQUENCY = "PURCHASE_FREQUENCY"
    PURCHASE_DATE = "PURCHASE_DATE"
    PURCHASE_DEPARTMENT = "PURCHASE_DEPARTMENT"
    NUTRISCORE = "NUTRISCORE"


class ProductAvailabilityStatus(Enum):
    NO_LONGER_IN_ASSORTMENT = auto()
    IN_ASSORTMENT = auto()
    FUTURE_ASSORTMENT = auto()
    NOT_IN_ASSORTMENT = auto()
    UNAVAILABLE = auto()
    UNKNOWN = auto()


class ShopType(Enum):
    AH = auto()
    GALL = auto()
    ETOS = auto()
    UNKNOWN = auto()


class DiscountType(Enum):
    AH = auto()
    GAKK = auto()
    AHOO = auto()
    ETOO = auto()
    GAOO = auto()
    UNKNOWN = auto()


class SegmentType(Enum):
    AH = auto()
    GAKK = auto()
    AHOO = auto()
    ETOO = auto()
    GAOO = auto()
    UNKNOWN = auto()


class BonusType(Enum):
    NATIONAL = auto()
    AHONLINE = auto()
    ETOS = auto()
    GALL = auto()
    PERPETUAL = auto()
    GALLCARD = auto()
    UNKNOWN = auto()


class ProductType(Enum):
    PRODUCT = auto()
    RETAILSET = auto()
    UNKNOWN = auto()
