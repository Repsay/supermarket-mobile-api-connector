from __future__ import annotations

import json
import os
import shutil
import tempfile
import typing
from typing import Any, Optional, Union, List, Dict

import requests
from requests.models import Response
from supermarket_connector import utils
from supermarket_connector.models.category import Category

# from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product
from unidecode import unidecode


class Client:
    BASE_URL = "https://webservice.aldi.nl/api/v1/"
    DEFAULT_HEADERS = {"User-Agent": "okhttp/3.9.0", "Content-Type": "application/json"}
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "ALDI")

    def __init__(self, debug: bool = False, debug_fn: Optional[str] = None, debug_value: bool = True) -> None:
        if not os.path.isdir(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)

        self.products = self.Products(self)
        self.categories = self.Categories(self)
        # self.images = self.Images(self)
        self.debug = debug
        self.debug_fn = debug_fn
        self.debug_value = debug_value

    def request(
        self,
        method: str,
        end_point: str,
        headers: Dict[str, Any] = {},
        params: Dict[str, Any] = {},
        timeout: int = 10,
        json_: bool = True,
        debug_key: Optional[str] = None,
    ) -> Union[str, List[Any], Dict[Any, Any]]:

        headers.update(self.DEFAULT_HEADERS)

        counter_tries = 0

        while True:
            try:
                counter_tries += 1
                response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout)

                if not response.ok:
                    print(f"Connection error: {response.status_code} try: {counter_tries}", end="\r")
                    if response.status_code == 404:
                        return {}
                    continue
            except Exception as e:
                print(e)
                continue
            else:
                break

        if json_:
            try:
                response_json: Union[List[Any], Dict[Any, Any]] = response.json()

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
                                    data: Dict[str, Any] = json.load(f)
                                    shutil.copyfile(debug_path, debug_path_temp)
                                except ValueError:
                                    data = {}
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

    class Categories:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: Dict[Union[int, str], Client.Category] = {}

        def list(self):
            response = self.__client.request("GET", "products.json")

            if not isinstance(response, dict):
                raise ValueError("Response is not in right format")

            collection: List[Dict[str, Any]] = response.get("productCollections", [])

            for elem in collection:
                id: Optional[str] = elem.get("id")

                if id is None:
                    print("expected ID")
                    continue

                category = self.__client.Category(self.__client, data=elem)

                if not category is None:
                    if not category.id in self.data.keys():
                        self.data[category.id] = category

            return self.data

    class Products:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: Dict[Union[int, str], Dict[int, Client.Product]] = {}

        @typing.overload
        def list(self) -> Dict[Union[int, str], Dict[int, Client.Product]]:
            ...

        @typing.overload
        def list(self, category: Client.Category) -> Dict[int, Client.Product]:
            ...

        def list(self, category: Optional[Client.Category] = None):
            if category is None:
                for category in self.__client.categories.list().values():
                    self.__client.products.list(category)
                    print(category.name)
                return self.data
            else:
                if self.data.get(category.id) is None:
                    self.data[category.id] = {}

                response = self.__client.request("GET", f"products/{category.id}.json", debug_key="products_info")

                if not isinstance(response, dict):
                    raise ValueError("Expected response to be dict")

                article_groups: Optional[List[Dict[str, Any]]] = response.get("articleGroups", [])

                article_groups = article_groups if not article_groups is None else []

                for group in article_groups:
                    for product in group.get("articles", []):
                        temp_ = self.__client.Product(self.__client, data=product, cat=category.id)
                        if not temp_ is None:
                            if not temp_.id in self.data[category.id].keys():
                                self.data[category.id][temp_.id] = temp_

                return self.data[category.id]

    class Category(Category):
        def __init__(
            self,
            client: Client,
            id: Optional[str] = None,
            name: Optional[str] = None,
            data: Optional[Dict[str, Any]] = None,
        ) -> None:
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing category need to have data or ID")

            slug_name = None
            has_products = False

            if not data is None:
                id = data.get("id")
                if id is None:
                    raise ValueError("Expected category to have ID")

                name = data.get("title")

                slug_name = unidecode(id.split("/")[-1])
                has_products: bool = data.get("hasProducts", False)

            if id is None:
                raise ValueError("Expected data to have ID")

            super().__init__(id, slug_name, name, False, has_products, images=[], subs=[])

    class Product(Product):
        def __init__(self, client: Client, id: Optional[str] = None, data: Optional[Dict[str, Any]] = None, cat: Optional[Union[str, int]] = None) -> None:
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing category need to have data or id")

            if not data is None:
                id = data.get("articleId")

            if id is None:
                raise ValueError("Expected data to have ID")

            super().__init__(id)

            if isinstance(cat, str):
                self.category = cat
            else:
                self.category_id = cat

            if not data is None:
                self.name = data.get("title")
                self.brand = data.get("brandName")
                self.available_online = not data.get("isNotAvailable", False) or not data.get("isSoldOut", False)
                self.order_availability_description = data.get("notAvailableText")

                price_raw = data.get("oldPriceFormatted")
                price_current = data.get("priceFormatted")

                self.price_raw = float(price_raw) if not price_raw is None else None
                self.price_current = float(price_current) if not price_current is None else None

                if not price_raw is None:
                    self.bonus = True
                    self.bonus_mechanism = data.get("priceReduction")

                self.unit_size = data.get("salesUnit")
                self.description = data.get("shortDescription")

        def details(self):
            print("No details to to show because all are available in the basic info")
            return self

        def price(self):
            if not self.price_current is None:
                return self.price_current
            return self.price_raw
