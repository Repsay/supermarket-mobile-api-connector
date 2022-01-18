from __future__ import annotations

import json
import math
import os
import shutil
import tempfile
import typing
from datetime import date
from typing import Any, Optional, Union

import requests
from requests.models import Response
from supermarket_connector import utils
from supermarket_connector.enums import ProductAvailabilityStatus, ProductType
from supermarket_connector.models.category import Category
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product
from unidecode import unidecode


class Client:
    BASE_URL = "https://mobileapi.jumbo.com/"
    DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0"}
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "JUMBO")

    def request(
        self, method: str, end_point: str, headers: dict[str, Any] = {}, params: dict[str, Any] = {}, timeout: int = 10, json_: bool = True, debug_key: Optional[str] = None
    ) -> Union[list[Any], dict[Any, Any], str]:

        headers.update(self.DEFAULT_HEADERS)

        while True:
            try:
                response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout)
            except Exception:
                continue
            else:
                break

        if not response.ok:
            if self.debug:
                print(f"Connection error: {response.status_code}")
            return self.request(method, end_point, headers, params, timeout, json_, debug_key)

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
                        debug_path_old = os.path.join(self.TEMP_DIR, self.debug_fn.replace(".json", "_old.json"))
                        if os.path.isfile(debug_path):
                            with open(debug_path, "r") as f:
                                try:
                                    data = json.load(f)
                                    shutil.copyfile(debug_path, debug_path_old)
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

    class Categories:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: dict[int, Client.Category] = {}

        def list(self):
            response = self.__client.request("GET", "v17/categories")

            if not isinstance(response, dict):
                raise ValueError("Reponse is not in right format")

            data: list[dict[Any, Any]] = response.get("categories", {}).get("data", [])

            for elem in data:
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
            self.data: dict[int, dict[str, Client.Product]] = {}

        @typing.overload
        def list(self) -> dict[int, dict[str, Client.Product]]:
            ...

        @typing.overload
        def list(self, category: Client.Category) -> dict[str, Client.Product]:
            ...

        def list(self, category: Optional[Client.Category] = None):
            if category is None:
                old_file_name = None
                for category in self.__client.categories.list().values():
                    if self.__client.debug_value:
                        old_file_name = self.__client.debug_fn
                        self.__client.debug_fn = f"{category.name}.json"
                    self.__client.products.list(category)
                    print(category.name)

                if not old_file_name is None:
                    self.__client.debug_fn = old_file_name

                return self.data
            else:
                total_pages = 0
                page = 0
                max_size = 30

                while True:
                    if self.data.get(category.id) is None:
                        self.data[category.id] = {}

                    response = self.__client.request("GET", "v17/search", params={"offset": page * max_size, "limit": max_size, "q": None, "filters": category.id})

                    if not isinstance(response, dict):
                        raise ValueError("Expected response to be dict")

                    if total_pages == 0:
                        total_pages: int = math.ceil(response.get("products", {}).get("total", 30) / max_size)

                    data: list[dict[Any, Any]] = response.get("products", {}).get("data", [])

                    for product in data:
                        temp_ = self.__client.Product(self.__client, data=product)
                        if not temp_ is None:
                            if not temp_.id in self.data[category.id].keys():
                                self.data[category.id][temp_.id] = temp_

                    page += 1

                    if page == total_pages:
                        break

                return self.data[category.id]

    class Images:
        def __init__(self, client: Client) -> None:
            self.__client = client

        def process(self, data: list[dict[str, Any]]):
            temp: list[Client.Image] = []
            for elem in data:
                temp.append(self.__client.Image(self.__client, data=elem))

            return temp

    class Product(Product):
        def __init__(self, client: Client, id: Optional[int] = None, data: Optional[dict[str, Any]] = None) -> None:
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing product need to have data or ID")

            if not data is None:
                id = data.get("id")

                if id is None:
                    raise ValueError("Expected data to have ID")

            super().__init__(id)

            if not data is None:
                images_data: list[dict[str, Any]] = data.get("imageInfo", {}).get("primaryView", [])
                quantity_data: dict[str, Any] = data.get("quantityOptions", [{}])[0]
                price_data: dict[str, Any] = data.get("prices", {})
                bonus_data: dict[str, Any] = data.get("promotion", {})

                self.name = data.get("title")
                self.unit_size = quantity_data.get("unit")
                self.default_amount = quantity_data.get("defaultAmount")
                self.minimum_amount = quantity_data.get("minimumAmount")
                self.amount_stepsize = quantity_data.get("amountStep")
                self.maximum_amount = quantity_data.get("maximumAmount")

                self.price_raw = price_data.get("price", {}).get("amount")
                if not self.price_raw is None:
                    self.price_raw = self.price_raw / 100

                self.price_current = price_data.get("promotionalPrice", {}).get("amount")
                if not self.price_current is None:
                    self.price_current = self.price_current / 100

                unit_size: Optional[str] = price_data.get("unitPrice", {}).get("unit")
                unit_size_price: Optional[Union[int, float]] = price_data.get("unitPrice", {}).get("price", {}).get("amount")
                if not unit_size_price is None:
                    unit_size_price = unit_size_price / 100

                self.unit_price_description = f"{unit_size_price} per {unit_size}"
                self.available_online = data.get("available", False)
                self.type = ProductType[data.get("productType", "UNKNOWN").upper()]
                self.nix18 = data.get("nixProduct", False)
                self.quantity = data.get("quantity")
                self.images = self.__client.images.process(images_data)

                self.bonus_start_date = date.fromtimestamp(bonus_data.get("fromDate", 0))
                self.bonus_end_date = date.fromtimestamp(bonus_data.get("toDate", 0))
                self.bonus_period_description = bonus_data.get("validityPeriod")
                self.bonus_segment_description = bonus_data.get("summary")
                self.bonus_mechanism = bonus_data.get("tags", [{}])[0].get("text")

                self.stickers = data.get("stickerBadges", [])
                self.sample = data.get("sample", False)
                self.order_availability = ProductAvailabilityStatus[data.get("unavailabilityReason", "IN_ASSORTMENT")]
                self.order_availability_description = data.get("reason")

                self.bonus = not data.get("promotion") is None
            else:
                raise ValueError("When initilizing category need to have data or id")

        def details(self):
            response = self.__client.request("GET", f"v17/products/{self.id}", debug_key="product_details")

            if not isinstance(response, dict):
                raise ValueError("Expected value to be dict")

            data: dict[str, Any] = response.get("product", {})
            productCard: dict[str, Any] = data.get("data", {})
            brand_data: dict[str, Any] = productCard.get("brandInfo", {})
            # alergy_data: list[str] = productCard.get("allergyText", "").split(",")

            self.category = productCard.get("topLevelCategory")
            self.category_id = productCard.get("topLevelCategoryId")
            self.description_extra = productCard.get("detailsText")
            self.sizing = productCard.get("numberOfServings", "").split("-")

            self.storage_advice = productCard.get("usageAndSafetyInfo", {}).get("storageType")
            self.country = productCard.get("originInfo", {}).get("countryOfOrigin")

            self.brand_description = brand_data.get("brandDescription")
            self.brand_address = brand_data.get("manufacturerAddress")
            self.brand_webaddress = brand_data.get("webAddress")
            self.brand_phone = brand_data.get("telephoneHelpline")

            return self

        def price(self):
            if not self.price_current is None:
                return self.price_current
            else:
                return self.price_raw

    class Category(Category):
        subs: list[Client.Category]
        images: list[Client.Image]

        def __init__(
            self,
            client: Client,
            id: Optional[int] = None,
            name: Optional[str] = None,
            image: Optional[Client.Image] = None,
            data: Optional[dict[str, Any]] = None,
        ) -> None:
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing category need to have data or ID")

            slug_name = None

            if not data is None:
                id = data.get("id")
                name = data.get("title")

                if not name is None:
                    slug_name = unidecode(name).lower().replace(",", "").replace(" ", "-")

                image = self.__client.Image(self.__client, url=data.get("imageUrl", ""))

            if id is None:
                raise ValueError("Expected data to have ID")

            id = int(id)

            super().__init__(id, slug_name, name, images=[image], subs=[])

        def list_subs(self, recursive: bool = True):
            response = self.__client.request("GET", f"v17/categories", params={"id": self.id})

            if not isinstance(response, dict):
                raise ValueError("Expected response to be dict")

            data = response.get("categories", {}).get("data", [])

            for elem in data:
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
            self.client = client

            height = None
            width = None

            if not data is None:
                url = data.get("url")
                height = data.get("height")
                width = data.get("width")

            if url is None:
                raise ValueError("Expected image url not to be None")

            super().__init__(url, height, width)
