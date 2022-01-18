from typing import Any, Optional, List
from supermarket_connector.enums import DiscountType, ProductAvailabilityStatus, BonusType, ProductType, SegmentType, ShopType

from datetime import date
from abc import ABC
import abc
import dataclasses


@dataclasses.dataclass
class Product(ABC):
    # Info
    id: Any
    name: Optional[str] = None
    brand: Optional[str] = None
    type: Optional[ProductType] = None
    shop_type: Optional[ShopType] = None
    category: Optional[str] = None
    category_id: Optional[str] = None
    subcategory: Optional[str] = None
    subcategory_id: Optional[str] = None
    nix18: bool = False
    nutriscore: Optional[str] = None
    sample: bool = False
    sponsored: bool = False

    # Images
    images: List[Any] = dataclasses.field(default_factory=lambda: [])
    icons: List[str] = dataclasses.field(default_factory=lambda: [])
    stickers: List[str] = dataclasses.field(default_factory=lambda: [])

    # Description
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_extra: Optional[str] = None

    # Price
    price_raw: Optional[float] = None
    price_current: Optional[float] = None
    unit_price_description: Optional[str] = None

    # Quantity
    unit_size: Optional[str] = None
    default_amount: Optional[int] = None
    minimum_amount: Optional[int] = None
    amount_stepsize: Optional[int] = None
    maximum_amount: Optional[int] = None
    quantity: Optional[str] = None

    # Order info
    order_availability: Optional[ProductAvailabilityStatus] = None
    order_availability_description: Optional[str] = None
    available_online: bool = True
    orderable: bool = True

    # Bonus
    bonus: bool = False
    bonus_price: bool = False
    bonus_infinite: bool = False
    bonus_start_date: Optional[date] = None
    bonus_end_date: Optional[date] = None
    bonus_type: Optional[BonusType] = None
    bonus_mechanism: Optional[str] = None
    bonus_period_description: Optional[str] = None
    stapel_bonus: bool = False
    discount_type: Optional[DiscountType] = None
    segment_type: Optional[SegmentType] = None
    bonus_segment_id: Optional[int] = None
    bonus_segment_description: Optional[str] = None

    # Bundle
    bundle: bool = False
    bundle_items: List[Any] = dataclasses.field(default_factory=lambda: [])

    # product details
    fragrance: List[str] = dataclasses.field(default_factory=lambda: [])
    taste: List[str] = dataclasses.field(default_factory=lambda: [])
    colour: List[str] = dataclasses.field(default_factory=lambda: [])
    grape: List[str] = dataclasses.field(default_factory=lambda: [])
    processing_type: List[str] = dataclasses.field(default_factory=lambda: [])
    processed_type: List[str] = dataclasses.field(default_factory=lambda: [])
    taste_experience: List[str] = dataclasses.field(default_factory=lambda: [])
    preparation_type: List[str] = dataclasses.field(default_factory=lambda: [])
    regionalism: List[str] = dataclasses.field(default_factory=lambda: [])
    sliced_method: List[str] = dataclasses.field(default_factory=lambda: [])
    sizing: List[str] = dataclasses.field(default_factory=lambda: [])
    grain_type: List[str] = dataclasses.field(default_factory=lambda: [])
    animal_species: List[str] = dataclasses.field(default_factory=lambda: [])
    egg_type: List[str] = dataclasses.field(default_factory=lambda: [])
    moments_of_use: List[str] = dataclasses.field(default_factory=lambda: [])
    maturity: List[str] = dataclasses.field(default_factory=lambda: [])
    fat_content: List[str] = dataclasses.field(default_factory=lambda: [])
    accreditation: List[str] = dataclasses.field(default_factory=lambda: [])
    quality_mark: List[str] = dataclasses.field(default_factory=lambda: [])
    form: List[str] = dataclasses.field(default_factory=lambda: [])
    product_type: List[str] = dataclasses.field(default_factory=lambda: [])
    packaging: List[str] = dataclasses.field(default_factory=lambda: [])
    kitchen: List[str] = dataclasses.field(default_factory=lambda: [])
    characteristic: List[str] = dataclasses.field(default_factory=lambda: [])
    store_department: List[str] = dataclasses.field(default_factory=lambda: [])
    special_occasion: List[str] = dataclasses.field(default_factory=lambda: [])
    freshness: List[str] = dataclasses.field(default_factory=lambda: [])
    application: List[str] = dataclasses.field(default_factory=lambda: [])
    carbonic_acid: List[str] = dataclasses.field(default_factory=lambda: [])
    carbonic_acid_intensity: List[str] = dataclasses.field(default_factory=lambda: [])
    taste_intensity: List[str] = dataclasses.field(default_factory=lambda: [])
    coffee_machine_type: List[str] = dataclasses.field(default_factory=lambda: [])
    bread_type: List[str] = dataclasses.field(default_factory=lambda: [])
    usage: List[str] = dataclasses.field(default_factory=lambda: [])
    closure_method: List[str] = dataclasses.field(default_factory=lambda: [])
    tasty_with: List[str] = dataclasses.field(default_factory=lambda: [])
    region: List[str] = dataclasses.field(default_factory=lambda: [])
    wash_type: List[str] = dataclasses.field(default_factory=lambda: [])
    liquid_solid: List[str] = dataclasses.field(default_factory=lambda: [])
    usage_location: List[str] = dataclasses.field(default_factory=lambda: [])
    taste_profile: List[str] = dataclasses.field(default_factory=lambda: [])
    amount_washes: List[str] = dataclasses.field(default_factory=lambda: [])
    age_usage: List[str] = dataclasses.field(default_factory=lambda: [])
    hair_type: List[str] = dataclasses.field(default_factory=lambda: [])
    skin_type: List[str] = dataclasses.field(default_factory=lambda: [])
    feed_type: List[str] = dataclasses.field(default_factory=lambda: [])
    connection_type: List[str] = dataclasses.field(default_factory=lambda: [])
    watt: List[str] = dataclasses.field(default_factory=lambda: [])
    tobacco: List[str] = dataclasses.field(default_factory=lambda: [])

    brand_description: Optional[str] = None
    brand_address: Optional[str] = None
    brand_webaddress: Optional[str] = None
    brand_phone: Optional[str] = None

    toilet_paper_layers: Optional[int] = None
    country: Optional[str] = None
    wine_type: Optional[str] = None
    storage_advice: Optional[str] = None

    sliced: bool = False
    bake_off: bool = False
    caffeine_free: bool = True
    sugar_free: bool = False
    local: bool = False
    alcohol_free: bool = True
    salted: bool = False
    cheap_option: bool = False
    new: bool = False
    amazingly_cheap: bool = False
    value_pack: bool = False
    pure_honest: bool = False
    freezer: bool = False
    party_favorite: bool = False
    ready: bool = False
    fairtrade: bool = False
    sustainable_catch: bool = False
    free_range_meat: bool = False
    greenfield: bool = False
    kids: bool = False
    elderly: bool = False
    soja_dairy: bool = False
    etos: bool = False
    men: bool = False
    women: bool = False
    dimmable: bool = False

    # dieet
    vegan: bool = False
    vegeterian: bool = False
    low_salt: bool = False
    organic: bool = False
    low_fat: bool = False
    halal: bool = False
    low_sugar: bool = False

    # intolerance
    celery_free: bool = True
    lobster_free: bool = True
    egg_free: bool = True
    fish_free: bool = True
    gluten_free: bool = True
    lactose_free: bool = True
    lupine_free: bool = True
    milk_free: bool = True
    shellfish_free: bool = True
    mustard_free: bool = True
    peanut_free: bool = True
    sesame_free: bool = True
    soja_free: bool = True
    sulfite_free: bool = True
    nuts_free: bool = True

    @abc.abstractclassmethod
    def price(self):
        pass
