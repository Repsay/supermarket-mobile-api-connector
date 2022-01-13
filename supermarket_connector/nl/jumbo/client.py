from __future__ import annotations

import json
import math
import os
import tempfile
from typing import Any, Optional, Union

import requests
from requests.models import Response
from supermarket_connector.models.category import Category
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product

# from supermarket_connector.nl.jumbo import errors
from supermarket_connector import utils

from unidecode import unidecode


class Client:
    BASE_URL = "https://mobileapi.jumbo.com/"
    DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0"}
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "JUMBO")

    def request(
        self,
        method: str,
        end_point: str,
        headers: dict[str, Any] = {},
        params: dict[str, Any] = {},
        timeout: int = 10,
        json_: bool = True,
    ) -> Union[str, Any]:

        headers.update(self.DEFAULT_HEADERS)

        response: Response = requests.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout)

        if not response.ok:
            response.raise_for_status()

        if json_:
            try:
                response_json = response.json()

                if self.debug:
                    if self.debug_fn is None:
                        print("To debug response also give a filename")
                    elif not self.debug_fn.endswith(".json"):
                        print("Currently only json format is supported")
                    else:
                        debug_path = os.path.join(self.TEMP_DIR, self.debug_fn)
                        if os.path.isfile(debug_path):
                            with open(debug_path, "r") as f:
                                data = json.load(f)
                        else:
                            data = {}

                        if not end_point in data.keys():
                            data[end_point] = {}

                        with open(debug_path, "w") as f:
                            if isinstance(response_json, list):
                                data[end_point] = utils.process_type(response_json, data[end_point], self.debug_value)
                                json.dump(data, f)
                            elif isinstance(response_json, dict):
                                data[end_point] = utils.type_def_dict(response_json, data[end_point], self.debug_value)
                                json.dump(data, f)
                            else:
                                print("Currently only list or dict format response supported")

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
            self.data: list[Client.Category] = []

        def list(self):
            response = self.__client.request("GET", "v17/categories")

            if not isinstance(response, dict):
                raise ValueError("Reponse is not in right format")

            data = response.get("categories", {}).get("data", [])

            for elem in data:
                if not isinstance(elem, dict):
                    raise ValueError("Expected dict")
                category = self.__client.Category(self.__client, data=elem)
                if not category is None:
                    self.data.append(category)

            return self.data

        def get(self, id: Optional[int] = None, name: Optional[str] = None):
            if not id is None:
                for category in self.data:
                    if category.id == id:
                        return category

                for category in self.list():
                    if category.id == id:
                        return category

            elif not name is None:
                for category in self.data:
                    lookup = category.lookup(name=name)
                    if not lookup is None:
                        return lookup

                for category in self.list():
                    lookup = category.lookup(name=name)
                    if not lookup is None:
                        return lookup

            return None

    class Products:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: list[Client.Product] = []

        def list(self, category: Optional[Client.Category] = None):
            if category is None:
                for category in self.__client.categories.list():
                    self.__client.products.list(category)
                return self.data
            else:
                total_pages = 0
                page = 0
                max_size = 30

                while True:
                    response = self.__client.request("GET", "v17/search", params={"offset": page * max_size, "limit": max_size, "query": None})

                    if not isinstance(response, dict):
                        raise ValueError("Expected response to be dict")

                    if total_pages == 0:
                        total_pages: int = math.ceil(response.get("products", {}).get("total", 30) / max_size)

                    for product in response.get("products", {}).get("data", []):
                        temp_ = self.__client.Product(self.__client, data=product)
                        if not temp_ is None:
                            self.data.append(temp_)

                    page += 1

                    if page == total_pages:
                        break

                return self.data

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
                images_data: list[dict[str, Any]] = data.get("imageInfo", {}).get("primaryView", [])

                id = data.get("id")

                if id is None:
                    raise ValueError("Expected data to have ID")

                self.id = id
                self.name = data.get("title")
                quantity_options = data.get("quantityOptions", {})
                self.unit_size = quantity_options.get("unit")
                self.images = self.__client.images.process(images_data)

            else:
                raise ValueError("When initilizing category need to have data or id")

        def details(self):
            response = self.__client.request("GET", f"mobile-services/product/detail/v4/fir/{self.id}")

            if not isinstance(response, dict):
                raise ValueError("Expected value to be dict")

            data: dict[str, Any] = response
            productCard = data.get("productCard", {})
            self.subcategory_id: Optional[int] = productCard.get("subCategoryId")

            properties = productCard.get("properties", {})

            self.fragrance: list[str] = properties.get("da_fragrance", [])
            self.taste: list[str] = properties.get("da_taste", [])
            self.processing_type: list[str] = properties.get("da_processing_type", [])
            self.taste_experience: list[str] = properties.get("da_a_taste_experience", [])
            self.preparation_type: list[str] = properties.get("da_a_type_of_preparation_cookware", [])
            self.sliced: bool = not len(properties.get("da_sliced", [])) == 0
            self.regionalism: list[str] = properties.get("da_regionalism", [])
            self.sliced_method: list[str] = properties.get("da_cutting_method", [])
            self.sizing: list[str] = properties.get("da_a_sizing", [])
            self.grain_type: list[str] = properties.get("da_type_of_grain", [])
            self.animal_species: list[str] = properties.get("da_animal_species", [])
            self.egg_type: list[str] = properties.get("da_type_of_egg", [])
            self.moments_of_use: list[str] = properties.get("da_moments_of_use", [])
            self.maturity: list[str] = properties.get("da_maturity", [])
            self.fat_content: list[str] = properties.get("da_fat_content", [])
            self.bake_off: bool = not len(properties.get("da_product_bake_off", [])) == 0

            self.store_department: list[str] = properties.get("da_store_department", [])

            self.caffeine_free = len(properties.get("da_free_of_caffeine", [])) == 0
            self.sugar_free: bool = properties.get("da_free_of_sugar", ["Nee"])[0] == "Ja"
            self.local = not len(properties.get("np_lokaal", [])) == 0
            self.alcohol_free: bool = properties.get("da_free_of_alcohol", ["Ja"])[0] == "Ja"
            self.salted: bool = properties.get("da_salted_or_not_salted", ["Ongezouten"])[0] == "Gezouten"

            # dieet
            self.vegan = not len(properties.get("sp_include_dieet_veganistisch", [])) == 0
            self.vegeterian = not len(properties.get("sp_include_dieet_vegetarisch", [])) == 0
            self.low_salt = not len(properties.get("sp_include_dieet_laag_zout", [])) == 0
            self.organic = not len(properties.get("sp_include_dieet_biologisch", [])) == 0
            self.low_fat = not len(properties.get("sp_include_dieet_laag_vet", [])) == 0
            self.halal = not len(properties.get("sp_exclude_dieet_halal", [])) == 0
            self.low_sugar = not len(properties.get("sp_include_dieet_laag_suiker", [])) == 0

            # intolerance
            self.celery_free = not len(properties.get("sp_include_intolerance_geen_selderij", [])) == 0
            self.lobster_free = not len(properties.get("sp_include_intolerance_geen_kreeftachtigen", [])) == 0
            self.egg_free = not len(properties.get("sp_include_intolerance_geen_eieren", [])) == 0
            self.fish_free = not len(properties.get("sp_include_intolerance_geen_vis", [])) == 0
            self.gluten_free = not len(properties.get("sp_include_intolerance_geen_gluten", [])) == 0
            self.lactose_free = not len(properties.get("sp_include_intolerance_geen_lactose", [])) == 0
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
            name: Optional[str] = None,
            image: Optional[Client.Image] = None,
            data: Optional[dict[str, Any]] = None,
        ) -> None:
            super().__init__()
            self.__client = client

            if data is None and not id is None:
                self.id = id
                if not name is None:
                    self.slug_name = unidecode(name).lower().replace(",", "").replace(" ", "-")
                else:
                    self.slug_name = None
                self.name = name
                self.image = image
            elif not data is None:

                id = data.get("id")
                if id is None:
                    raise ValueError("Expected data to have ID")

                self.id = int(id)
                self.name: Optional[str] = data.get("title")
                if not self.name is None:
                    self.slug_name = unidecode(self.name).lower().replace(",", "").replace(" ", "-")
                else:
                    self.slug_name = None
                self.image = self.__client.Image(self.__client, url=data.get("imageUrl", ""))
            else:
                raise ValueError("When initilizing category need to have data or id")

            self.subs: list[Client.Category] = []

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

            if not url is None:
                self.url = url
            elif not data is None:
                self.url = data.get("url")

                if self.url is None:
                    raise ValueError("Expected image url not to be None")

                self.width = data.get("width")
                self.height = data.get("height")
            else:
                raise ValueError("When initilizing image need to have data or url")


if __name__ == "__main__":
    client = Client(True, "data.json")
    for elem in client.categories.list():
        for elem2 in elem.list_subs():
            print(elem2.slug_name)

    # print(client.categories.data[0])
    # print(client.products.list(client.categories.data[0]))
    # # print(client.products.list(client.categories.data[0]))
    # print(client.products.data[0].details())
