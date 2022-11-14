from __future__ import annotations

import json
import math
import os
import shutil
import tempfile
import typing
from typing import Any, Optional, Union, List, Dict

import requests
from requests.models import Response
from supermarket_connector import utils
from supermarket_connector.models.category import Category
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product


class Client:
    BASE_URL = "https://api.coop.nl/INTERSHOP/rest/WFS/COOP-COOPBase-Site/-;loc=nl_NL;cur=EUR/"
    DEFAULT_HEADERS = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "COOP")

    access_token: Optional[str] = None

    def request(
        self,
        method: str,
        end_point: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        timeout: int = 10,
        json_: bool = True,
        debug_key: Optional[str] = None,
    ) -> Union[str, List[Any], Dict[Any, Any]]:
        if headers is None:
            headers = {}

        if params is None:
            params = {}

        headers.update(self.DEFAULT_HEADERS)

        while True:
            try:
                if not request_data is None:
                    response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, data=json.dumps(request_data), timeout=timeout)
                else:
                    response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout)
            except Exception:
                continue
            else:
                break

        if not response.ok:
            response.raise_for_status()

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
            self.data: Dict[Union[int, str], Client.Category] = {}

        def list(self):
            response = self.__client.request("GET", "categories/boodschappen")

            if not isinstance(response, dict):
                raise ValueError("Reponse is not in right format")

            data = response.get("subCategories", [])

            for elem in data:
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
            self.data: Dict[Union[int, str], Dict[int, Client.Product]] = {}

        @typing.overload
        def list(self) -> Dict[Union[int, str], Dict[int, Client.Product]]:
            ...

        @typing.overload
        def list(self, category: Client.Category) -> Dict[int, Client.Product]:
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
                    print(f"{page + 1}/{total_pages}", end="\r")
                    response = self.__client.request("GET", f"categories/boodschappen/{category.id}/products", params={"offset": page * 20, "amount": 20, "attrs": "sku,salePrice,listPrice,availability,manufacturer,image,minOrderQuantity,inStock,promotions,packingUnit,mastered,productMaster,productMasterSKU,roundedAverageRating,longtail,sticker,maxXLabel,Inhoud"})

                    if not isinstance(response, dict):
                        raise ValueError("Expected response to be dict")

                    if total_pages == 0:
                        total_pages: int = math.ceil(int(response.get("total", 0)) / 20)

                    for product in response.get("elements", []):
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

        def process(self, data: List[Dict[str, Any]]):
            temp: List[Client.Image] = []
            for elem in data:
                temp.append(self.__client.Image(self.__client, data=elem))

            return temp

    class Product(Product):
        def __init__(self, client: Client, id: Optional[Union[int, str]] = None, data: Optional[Dict[str, Any]] = None) -> None:
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing category need to have data or id")

            if not data is None:
                attributes = data.get("attributes", [])

                for attribute in attributes:
                    if attribute.get("name") == "sku":
                        id = attribute.get("value")
                        break

                if id is None:
                    raise ValueError("Expected data to have ID")

                if not isinstance(id, int) and id.isdigit():
                    id = int(id)

            super().__init__(id)

            if not data is None:
                self.name = data.get("title")
                self.description = data.get("description")
                attributes: List[Dict[str, Any]] = data.get("attributes", [])
                for attribute in attributes:
                    self.order_availability = attribute.get("value") if attribute.get("name") == "availability" else self.order_availability
                    self.brand_description = attribute.get("value") if attribute.get("name") == "manufacturer" else self.brand_description

                    if attribute.get("name") == "listPrice":
                        data = attribute.get("value", {})
                        if data is None:
                            continue
                        self.price_raw = data.get("value")

                    if attribute.get("name") == "salePrice":
                        data = attribute.get("value", {})
                        if data is None:
                            continue
                        self.price_current = data.get("value")


                if self.price_raw is None:
                    self.price_raw = self.price_current

                if self.price_current is None:
                    self.price_current = self.price_raw

                if self.price_raw != self.price_current:
                    self.bonus = True

        def details(self):
            response = self.__client.request("GET", f"products/{self.id}", debug_key="product_details")

            if not isinstance(response, dict):
                raise ValueError("Expected value to be dict")

            data: Dict[str, Any] = response
            attributes = data.get("attributes", [])

            for attribute in attributes:
                if attribute.get("name") == "Inhoud":
                    self.unit_size = attribute.get("value")

                self.description = attribute.get("value") if attribute.get("name") == "longDescription" else self.description
                self.description_extra = attribute.get("value") if attribute.get("name") == "shortDescription" else self.description_extra


            return self

        def price(self): # type: ignore
            if not self.price_current is None:
                return self.price_current
            else:
                return self.price_raw

    class Category(Category):
        subs: List[Client.Category]
        images: List[Client.Image]

        def __init__(
            self,
            client: Client,
            id: Optional[int] = None,
            slug_name: Optional[str] = None,
            name: Optional[str] = None,
            nix18: bool = False,
            images: List[Client.Image] = [],
            data: Optional[Dict[str, Any]] = None,
        ) -> None:
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing category need to have data or id")

            if not data is None:
                id = data.get("id")

                slug_name = data.get("slugifiedName")
                name = data.get("name")
                nix18 = data.get("nix18", False)
                images = self.__client.images.process(data.get("images", []))

            if id is None:
                raise ValueError("Expected data to have ID")

            super().__init__(id, slug_name, name, nix18, True, images, [])

        def list_subs(self, recursive: bool = True):
            response = self.__client.request("GET", f"mobile-services/v1/product-shelves/categories/{self.id}/sub-categories", debug_key="list_subcategories")

            if not isinstance(response, dict):
                raise ValueError("Expected response to be dict")

            children: List[Dict[str, Any]] = response.get("children", [])

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
            data: Optional[Dict[str, Any]] = None,
        ) -> None:
            self.__client = client

            height = None
            width = None

            if not data is None:
                url = data.get("effectiveUrl")
                height = data.get("imageActualHeight")
                width = data.get("imageActualWidth")

            if url is None:
                raise ValueError("Expected image url not to be None")

            super().__init__(url, height, width)
