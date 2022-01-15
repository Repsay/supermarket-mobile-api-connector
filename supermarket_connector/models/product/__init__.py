from typing import Any, Optional
from supermarket_connector.enums import DiscountType, ProductAvailabilityStatus, BonusType, ProductType, SegmentType, ShopType

from datetime import date

from abc import ABC, abstractclassmethod


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
    images: list[Any] = []
    icons: list[str] = []
    stickers: list[str] = []

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
    bundle_items: list[Any] = []

    # product details
    fragrance: list[str] = []
    taste: list[str] = []
    colour: list[str] = []
    grape: list[str] = []
    processing_type: list[str] = []
    processed_type: list[str] = []
    taste_experience: list[str] = []
    preparation_type: list[str] = []
    regionalism: list[str] = []
    sliced_method: list[str] = []
    sizing: list[str] = []
    grain_type: list[str] = []
    animal_species: list[str] = []
    egg_type: list[str] = []
    moments_of_use: list[str] = []
    maturity: list[str] = []
    fat_content: list[str] = []
    accreditation: list[str] = []
    quality_mark: list[str] = []
    form: list[str] = []
    product_type: list[str] = []
    packaging: list[str] = []
    kitchen: list[str] = []
    characteristic: list[str] = []
    store_department: list[str] = []
    special_occasion: list[str] = []
    freshness: list[str] = []
    application: list[str] = []
    carbonic_acid: list[str] = []
    carbonic_acid_intensity: list[str] = []
    taste_intensity: list[str] = []
    coffee_machine_type: list[str] = []
    bread_type: list[str] = []
    usage: list[str] = []
    closure_method: list[str] = []
    tasty_with: list[str] = []
    region: list[str] = []
    wash_type: list[str] = []
    liquid_solid: list[str] = []
    usage_location: list[str] = []
    taste_profile: list[str] = []
    amount_washes: list[str] = []
    age_usage: list[str] = []
    hair_type: list[str] = []
    skin_type: list[str] = []
    feed_type: list[str] = []
    connection_type: list[str] = []
    watt: list[str] = []
    tobacco: list[str] = []

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

    @abstractclassmethod
    def __init__(self) -> None:
        pass

    @abstractclassmethod
    def price(self):
        pass
