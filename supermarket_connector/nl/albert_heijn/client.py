from __future__ import annotations

import json
import os
import shutil
import tempfile
import typing
from datetime import date
from typing import Any, Optional, Union

import requests
from requests.models import Response
from supermarket_connector import utils
from supermarket_connector.enums import BonusType, DiscountType, ProductAvailabilityStatus, SegmentType, ShopType
from supermarket_connector.models.category import Category
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product
from supermarket_connector.nl.albert_heijn import errors


class Client:
    BASE_URL = "https://ms.ah.nl/"
    DEFAULT_HEADERS = {"User-Agent": "android/6.29.3 Model/phone Android/7.0-API24", "Host": "ms.ah.nl"}
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "AH")

    access_token: Optional[str] = None

    def get_anonymous_access_token(self) -> Optional[str]:
        response = self.request("POST", "create-anonymous-member-token", params={"client": "appie-anonymous"}, authorized=False)

        if not isinstance(response, dict):
            raise ValueError("Expected JSON")

        self.access_token = response.get("access_token")

    def request(
        self, method: str, end_point: str, headers: dict[str, Any] = {}, params: dict[str, Any] = {}, timeout: int = 10, authorized: bool = True, json_: bool = True, debug_key: Optional[str] = None
    ) -> Union[str, list[Any], dict[Any, Any]]:

        headers.update(self.DEFAULT_HEADERS)

        if authorized:
            if self.access_token is None:
                raise errors.AuthenticationError("Need token to make authorized requests")
            headers["Authorization"] = f"Bearer {self.access_token}"

        while True:
            try:
                response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout)
            except Exception:
                continue
            else:
                break

        if not response.ok:
            if response.status_code == 401:
                self.get_anonymous_access_token()

            if not self.access_token is None:
                if self.debug:
                    print(f"Connection error: {response.status_code}")
                return self.request(method, end_point, headers, params, timeout, authorized, json_, debug_key)

            response.raise_for_status()

        if json_:
            try:
                response_json: Union[list[Any], dict[Any, Any]] = response.json()

                if self.debug:
                    if self.debug_fn is None:
                        print("To debug response also give a filename")
                    elif not self.debug_fn.endswith(".json"):
                        print("Currently only json format is supported")
                    else:
                        debug_path = os.path.join(self.TEMP_DIR, self.debug_fn)
                        debug_path_temp = os.path.join(self.TEMP_DIR, self.debug_fn.replace(".json", "_old.json"))
                        if os.path.isfile(debug_path):
                            with open(debug_path, "r") as f:
                                try:
                                    data: dict[str, Any] = json.load(f)
                                    shutil.copyfile(debug_path, debug_path_temp)
                                except ValueError:
                                    data = {}
                                    pass
                        else:
                            data = {}

                        if not debug_key in data.keys() and not debug_key is None:
                            data[debug_key] = {}

                        if not end_point in data.keys() and debug_key is None:
                            data[end_point] = {}

                        if not debug_key is None:
                            key = debug_key
                        else:
                            key = end_point

                        with open(debug_path, "w") as f:
                            if isinstance(response_json, list):
                                data[key] = utils.process_type(response_json, data[key], self.debug_value)
                                json.dump(data, f)
                            else:
                                data[key] = utils.type_def_dict(response_json, data[key], self.debug_value)
                                json.dump(data, f)

                return response_json
            except ValueError:
                raise ValueError("Response is not in JSON format")
        else:
            return response.text

    def __init__(
        self,
        debug: bool = False,
        debug_fn: Optional[str] = None,
        debug_value: bool = True,
    ) -> None:
        if not os.path.isdir(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)

        self.products = self.Products(self)
        self.categories = self.Categories(self)
        self.images = self.Images(self)
        self.debug = debug
        self.debug_fn = debug_fn
        self.debug_value = debug_value
        self.get_anonymous_access_token()

    class Categories:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: dict[int, Client.Category] = {}

        def list(self):
            response = self.__client.request("GET", "mobile-services/v1/product-shelves/categories")

            if not isinstance(response, list):
                raise ValueError("Reponse is not in right format")

            for elem in response:
                if not isinstance(elem, dict):
                    raise ValueError("Expected dict")
                category = self.__client.Category(self.__client, data=elem)
                if not category is None:
                    if not category.id in self.data.keys():
                        self.data[category.id] = category

            return self.data

        def get(self, id: Optional[int] = None, name: Optional[str] = None):
            if not id is None:
                if id in self.data.keys():
                    self.data[id]

                self.list()

                if id in self.data.keys():
                    self.data[id]

            elif not name is None:
                for category in self.data.values():
                    lookup = category.lookup(name=name)
                    if not lookup is None:
                        return lookup

                for category in self.list().values():
                    lookup = category.lookup(name=name)
                    if not lookup is None:
                        return lookup

            return None

    class Products:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: dict[int, dict[int, Client.Product]] = {}

        @typing.overload
        def list(self) -> dict[int, dict[int, Client.Product]]:
            ...

        @typing.overload
        def list(self, category: Client.Category) -> dict[int, Client.Product]:
            ...

        def list(self, category: Optional[Client.Category] = None):
            if category is None:
                old_file_name = None
                for category in self.__client.categories.list().values():
                    if self.__client.debug_value:
                        old_file_name = self.__client.debug_fn
                        self.__client.debug_fn = f"product_{category.name}.json"
                    self.__client.products.list(category)
                    print(category.name)

                if not old_file_name is None:
                    self.__client.debug_fn = old_file_name

                return self.data
            else:
                sub_category = False
                total_pages = 0
                page = 0

                if self.data.get(category.id) is None:
                    self.data[category.id] = {}

                while True:
                    response = self.__client.request("GET", "mobile-services/product/search/v2", params={"page": page, "size": 1000, "query": None, "taxonomyId": category.id})

                    if not isinstance(response, dict):
                        raise ValueError("Expected response to be dict")

                    if total_pages == 0:
                        total_pages: int = int(response.get("page", {}).get("totalPages", 1))

                    if total_pages > 3:
                        sub_category = True
                        break

                    for product in response.get("products", []):
                        temp_ = self.__client.Product(self.__client, data=product)
                        if not temp_ is None:
                            if not temp_.id in self.data[category.id].keys():
                                self.data[category.id][temp_.id] = temp_

                    page += 1

                    if page == total_pages:
                        break

                if sub_category:
                    for sub_category in category.list_subs(False):
                        data = self.list(sub_category)

                        self.data[category.id].update(data)

                return self.data[category.id]

    class Images:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: list[Client.Image] = []

        def process(self, data: list[dict[str, Any]]):
            for elem in data:
                self.data.append(self.__client.Image(self.__client, data=elem))

            return self.data

    class Product(Product):
        def __init__(self, client: Client, id: Optional[int] = None, data: Optional[dict[str, Any]] = None) -> None:
            super().__init__()
            self.__client = client

            if data is None and not id is None:
                self.id = id
            elif not data is None:
                images_data: list[dict[str, Any]] = data.get("images", [])
                start_date_raw = data.get("bonusStartDate")
                end_date_raw = data.get("bonusEndDate")
                bonus_type_raw = data.get("promotionType")
                discount_type_raw = data.get("discountType")
                segment_type_raw = data.get("segmentType")

                id = data.get("webshopId")

                if id is None:
                    raise ValueError("Expected data to have ID")

                self.id = id
                self.name = data.get("title")
                self.brand = data.get("brand")
                self.shop_type = ShopType[data.get("shopType", "UNKNOWN")]
                self.category = data.get("mainCategory")
                self.subcategory = data.get("subCategory")
                self.nix18 = data.get("nix18", False)
                self.nutriscore = data.get("nutriscore")
                self.sample = data.get("isSample", False)
                self.sponsored = data.get("isSponsored", False)

                self.images: list[Client.Image] = self.__client.images.process(images_data)
                self.icons = data.get("propertyIcons", [])
                self.stickers = data.get("stickers", [])

                self.description = data.get("descriptionFull")
                self.description_html = data.get("descriptionHighlights")
                self.description_extra = data.get("extraDescriptions")

                self.price_raw = data.get("priceBeforeBonus")
                self.price_current = data.get("currentPrice")
                self.unit_price_description = data.get("unitPriceDescription")

                self.unit_size = data.get("salesUnitSize")

                self.order_availability = ProductAvailabilityStatus[data.get("orderAvailabilityStatus", "UNKNOWN")]
                self.order_availability_description = data.get("orderAvailabilityDescription")
                self.available_online = data.get("availableOnline", False)
                self.orderable = data.get("isOrderable", False)

                self.bonus = data.get("isBonus", False)
                self.bonus_price = data.get("isBonusPrice", False)
                self.bonus_infinite = data.get("isInfiniteBonus", False)
                self.bonus_start_date = date.fromisoformat(start_date_raw) if not start_date_raw is None else None
                self.bonus_end_date = date.fromisoformat(end_date_raw) if not end_date_raw is None else None
                self.bonus_type = BonusType[bonus_type_raw] if not bonus_type_raw is None else None
                self.bonus_mechanism = data.get("bonusMechanism")
                self.bonus_period_description = data.get("bonusPeriodDescription")
                self.stapel_bonus = data.get("isStapelBonus", False)
                self.discount_type = DiscountType[discount_type_raw] if not discount_type_raw is None else None
                self.segment_type = SegmentType[segment_type_raw] if not segment_type_raw is None else None
                self.bonus_segment_id = data.get("bonusSegmentId")
                self.bonus_segment_description = data.get("bonusSegmentDescription")

                self.bundle = data.get("isVirtualBundle", False)
                self.bundle_items = data.get("virtualBundleItems", [])

            else:
                raise ValueError("When initilizing category need to have data or id")

        def details(self):
            response = self.__client.request("GET", f"mobile-services/product/detail/v4/fir/{self.id}", debug_key="product_details")

            if not isinstance(response, dict):
                raise ValueError("Expected value to be dict")

            data: dict[str, Any] = response
            productCard: dict[str, Any] = data.get("productCard", {})
            self.subcategory_id = productCard.get("subCategoryId")
            self.description_extra = "\n".join(productCard.get("extraDescriptions", []))

            properties: dict[str, Any] = productCard.get("properties", {})

            self.fragrance = properties.get("da_fragrance", [])

            smaak: list[str] = properties.get("np_smaak", [])
            self.taste = properties.get("da_taste", [])
            self.taste.extend(smaak)

            kleur: list[str] = properties.get("np_kleur", [])
            self.colour = properties.get("da_colour", [])
            self.colour.extend(kleur)

            druivenras: list[str] = properties.get("np_druivenras", [])
            self.grape = properties.get("da_grape", [])
            self.grape.extend(druivenras)

            self.processing_type = properties.get("da_processing_type", [])
            self.processed_type = properties.get("da_type_of_processed_food", [])
            self.taste_experience = properties.get("da_a_taste_experience", [])
            self.preparation_type = properties.get("da_a_type_of_preparation_cookware", [])
            self.regionalism = properties.get("da_regionalism", [])
            self.sliced_method = properties.get("da_cutting_method", [])
            self.sizing = properties.get("da_a_sizing", [])
            self.grain_type = properties.get("da_type_of_grain", [])
            self.animal_species = properties.get("da_animal_species", [])
            self.egg_type = properties.get("da_type_of_egg", [])
            self.moments_of_use = properties.get("da_moments_of_use", [])

            maturation: list[str] = properties.get("np_rijping", [])
            self.maturity = properties.get("da_maturity", [])
            self.maturity.extend(maturation)

            vetgehalte: list[str] = properties.get("np_vetgehalte", [])
            self.fat_content = properties.get("da_fat_content", [])
            self.fat_content.extend(vetgehalte)

            self.accreditation = properties.get("da_accreditation", [])
            self.quality_mark = properties.get("da_quality_mark", [])
            self.characteristic = properties.get("sp_kenmerk", [])
            self.form = properties.get("np_vorm", [])
            self.packaging = properties.get("np_verpakking", [])
            self.product_type = properties.get("np_soort", [])
            self.kitchen = properties.get("np_keuken", [])
            self.special_occasion = properties.get("np_seizoen", [])
            self.freshness = properties.get("np_versheid", [])
            self.application = properties.get("np_toepassing", [])
            self.carbonic_acid = properties.get("np_koolzuur", [])
            self.carbonic_acid_intensity = properties.get("da_carbonation_intensity", [])
            self.taste_intensity = properties.get("da_taste_intensity", [])
            self.coffee_machine_type = properties.get("da_type_of_coffee_machine", [])
            self.bread_type = properties.get("da_type_of_bread", [])

            recommended_usage: list[str] = properties.get("da_recommended_usage", [])
            self.usage = properties.get("da_usage", [])
            self.usage.extend(recommended_usage)

            self.closure_method = properties.get("da_closure_method", [])
            self.tasty_with = properties.get("da_tasty_with", [])

            streek: list[str] = properties.get("np_streek", [])
            self.region = properties.get("da_region", [])
            self.region.extend(streek)

            self.wash_type = properties.get("da_type_of_washes", [])
            self.liquid_solid = properties.get("da_liquid_solid", [])
            self.usage_location = properties.get("da_recommended_usage_loc", [])
            self.taste_profile = properties.get("da_bis_smaakprofiel", [])
            self.amount_washes = properties.get("da_amount_of_washes", [])
            self.age_usage = properties.get("np_leeftijd", [])
            self.hair_type = properties.get("da_type_of_hair", [])
            self.skin_type = properties.get("da_type_of_skin", [])
            layers: Optional[str] = properties.get("da_toilet_paper_layers")
            self.toilet_paper_layers = int(layers) if not layers is None else None
            self.feed_type = properties.get("da_type_of_feed", [])
            self.connection_type = properties.get("da_type_of_connection", [])
            self.watt = properties.get("da_watt", [])
            self.tobacco = properties.get("np_tabak", [])

            self.store_department = properties.get("da_store_department", [])

            self.nutriscore = properties.get("nutriscore", [None])[0]

            self.country = properties.get("da_country", [None])[0]
            if self.country is None:
                self.country = properties.get("np_land", [None])[0]

            self.wine_type = properties.get("da_wine_type", [None])[0]

            self.sliced = not len(properties.get("da_sliced", [])) == 0
            self.bake_off = not len(properties.get("da_product_bake_off", [])) == 0
            self.caffeine_free = len(properties.get("da_free_of_caffeine", [])) == 0

            self.sugar_free = properties.get("da_free_of_sugar", ["Nee"])[0] == "Ja"
            if not self.sugar_free:
                self.sugar_free = not len(properties.get("np_suikervrij", [])) == 0

            self.local = not len(properties.get("np_lokaal", [])) == 0
            self.alcohol_free = properties.get("da_free_of_alcohol", ["Ja"])[0] == "Ja"
            self.salted = properties.get("da_salted_or_not_salted", ["Ongezouten"])[0] == "Gezouten"
            self.cheap_option = not len(properties.get("np_goedkoopje", [])) == 0

            self.new = not len(properties.get("np_nieuw_2", [])) == 0
            if not self.new:
                self.new = not len(properties.get("np_nieuw", [])) == 0

            self.amazingly_cheap = not len(properties.get("np_verbluffen", [])) == 0
            self.value_pack = not len(properties.get("np_voordeel", [])) == 0
            self.pure_honest = not len(properties.get("np_puureerlij", [])) == 0
            self.freezer = not len(properties.get("diepvries", [])) == 0
            self.party_favorite = not len(properties.get("np_feestfav", [])) == 0
            self.ready = not len(properties.get("np_kant+klaar", [])) == 0
            self.fairtrade = not len(properties.get("np_fairtrade", [])) == 0
            self.sustainable_catch = not len(properties.get("np_duurzaam", [])) == 0
            self.free_range_meat = not len(properties.get("np_scharrel", [])) == 0
            self.greenfield = not len(properties.get("np_greenfield", [])) == 0
            self.kids = not len(properties.get("np_kids", [])) == 0
            self.elderly = not len(properties.get("np_ouderen", [])) == 0
            self.soja_dairy = not len(properties.get("np_sojazuivel", [])) == 0
            self.etos = not len(properties.get("np_etos", [])) == 0
            self.men = not len(properties.get("np_man", [])) == 0
            self.women = not len(properties.get("np_vrouw", [])) == 0
            self.dimmable = not len(properties.get("da_dim_function", [])) == 0

            # dieet
            self.vegan = not len(properties.get("sp_include_dieet_veganistisch", [])) == 0

            self.vegeterian = not len(properties.get("sp_include_dieet_vegetarisch", [])) == 0
            if not self.vegeterian:
                self.vegeterian = not len(properties.get("np_vegetarisc", [])) == 0

            self.low_salt = not len(properties.get("sp_include_dieet_laag_zout", [])) == 0
            self.organic = not len(properties.get("sp_include_dieet_biologisch", [])) == 0
            self.low_fat = not len(properties.get("sp_include_dieet_laag_vet", [])) == 0
            self.halal = not len(properties.get("sp_include_dieet_halal", [])) == 0
            self.low_sugar = not len(properties.get("sp_include_dieet_laag_suiker", [])) == 0
            if not self.low_sugar:
                self.low_sugar = not len(properties.get("np_suikergeha", [])) == 0

            # intolerance
            self.celery_free = not len(properties.get("sp_include_intolerance_geen_selderij", [])) == 0
            self.lobster_free = not len(properties.get("sp_include_intolerance_geen_kreeftachtigen", [])) == 0
            self.egg_free = not len(properties.get("sp_include_intolerance_geen_eieren", [])) == 0
            self.fish_free = not len(properties.get("sp_include_intolerance_geen_vis", [])) == 0
            self.gluten_free = not len(properties.get("sp_include_intolerance_geen_gluten", [])) == 0

            self.lactose_free = not len(properties.get("sp_include_intolerance_geen_lactose", [])) == 0
            if not self.lactose_free:
                self.lactose_free = not len(properties.get("np_lactose", [])) == 0

            self.lupine_free = not len(properties.get("sp_include_intolerance_geen_lupine", [])) == 0
            self.milk_free = not len(properties.get("sp_include_intolerance_geen_melk", [])) == 0
            self.shellfish_free = not len(properties.get("sp_include_intolerance_geen_schelpdieren", [])) == 0
            self.mustard_free = not len(properties.get("sp_include_intolerance_geen_mosterd", [])) == 0
            self.peanut_free = not len(properties.get("sp_include_intolerance_geen_pindas", [])) == 0
            self.sesame_free = not len(properties.get("sp_include_intolerance_geen_sesam", [])) == 0
            self.soja_free = not len(properties.get("sp_include_intolerance_geen_soja", [])) == 0
            self.sulfite_free = not len(properties.get("sp_include_intolerance_geen_sulfiet", [])) == 0
            self.nuts_free = not len(properties.get("sp_include_intolerance_geen_noten", [])) == 0

            return self

        def price(self):
            if not self.price_current is None:
                return self.price_current
            else:
                return self.price_raw

    class Category(Category):
        def __init__(
            self,
            client: Client,
            id: Optional[int] = None,
            slug_name: Optional[str] = None,
            name: Optional[str] = None,
            nix18: bool = False,
            images: list[Client.Image] = [],
            data: Optional[dict[str, Any]] = None,
        ) -> None:
            super().__init__()
            self.__client = client

            if data is None and not id is None:
                self.id = id
                self.slug_name = slug_name
                self.name = name
                self.nix18 = nix18
                self.images = images
            elif not data is None:
                images_data: list[dict[str, Any]] = data.get("images", [])

                id = data.get("id")
                if id is None:
                    raise ValueError("Expected data to have ID")

                self.id = id
                self.slug_name: Optional[str] = data.get("slugifiedName")
                self.name: Optional[str] = data.get("name")
                self.nix18: bool = data.get("nix18", False)
                self.images = self.__client.images.process(images_data)
            else:
                raise ValueError("When initilizing category need to have data or id")

            self.subs: list[Client.Category] = []

        def list_subs(self, recursive: bool = True):
            response = self.__client.request("GET", f"mobile-services/v1/product-shelves/categories/{self.id}/sub-categories", debug_key="list_subcategories")

            if not isinstance(response, dict):
                raise ValueError("Expected response to be dict")

            children: list[dict[str, Any]] = response.get("children", [])

            for elem in children:
                cat = self.__client.Category(self.__client, data=elem)
                if not cat is None:
                    if recursive:
                        cat.list_subs()
                    self.subs.append(cat)

            return self.subs

        def lookup(self, id: Optional[int] = None, name: Optional[str] = None) -> Optional[Client.Category]:
            if not id is None:
                if self.id == id:
                    return self
                else:
                    for sub in self.subs:
                        lookup = sub.lookup(id=id)
                        if not lookup is None:
                            return lookup

                    for sub in self.list_subs(False):
                        lookup = sub.lookup(id=id)
                        if not lookup is None:
                            return lookup

                    return None
            elif not name is None:
                if self.name == name:
                    return self
                else:
                    for sub in self.subs:
                        lookup = sub.lookup(name=name)
                        if not lookup is None:
                            return lookup

                    for sub in self.list_subs(False):
                        lookup = sub.lookup(name=name)
                        if not lookup is None:
                            return lookup

                    return None
            else:
                return None

    class Image(Image):
        def __init__(
            self,
            client: Client,
            url: Optional[str] = None,
            data: Optional[dict[str, Any]] = None,
        ) -> None:
            super().__init__()
            self.__client = client

            if not url is None:
                self.url = url
            elif not data is None:
                self.url = data.get("url")

                if self.url is None:
                    raise ValueError("Expected image url not to be None")

                self.width = data.get("width")
                self.height = data.get("height")
            else:
                raise ValueError("When initilizing category need to have data or url")
