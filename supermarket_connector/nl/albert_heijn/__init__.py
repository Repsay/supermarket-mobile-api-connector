from __future__ import annotations

import json
import os
import shutil
import tempfile
import typing
from datetime import date
from typing import Any, Optional, Union, List, Dict

import requests
from requests.models import Response
from supermarket_connector import utils
from supermarket_connector.enums import BonusType, DiscountType, ProductAvailabilityStatus, SegmentType, ShopType
from supermarket_connector.models.category import Category
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product
from supermarket_connector.nl.albert_heijn import errors


class Client:
    """Description of Client"""

    BASE_URL = "https://api.ah.nl/"
    DEFAULT_HEADERS = {
        "User-Agent": "android/6.29.3 Model/phone Android/7.0-API24",
        "Host": "api.ah.nl",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "AH")

    access_token: Optional[str] = None

    def get_anonymous_access_token(self) -> Optional[str]:
        """
        The get_anonymous_access_token function returns an anonymous access token.

        :returns: A string containing the access token, or None if no anonymous access token is available.

        :param self: Used to access the instance of the class.
        :return: a string.

        :doc-author: Trelent
        """
        response = self.request("POST", "mobile-auth/v1/auth/token/anonymous", request_data={"clientId": "appie"}, authorized=False)

        if not isinstance(response, dict):
            raise ValueError("Expected JSON")

        self.access_token = response.get("access_token")

    def request(
        self,
        method: str,
        end_point: str,
        headers: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        timeout: int = 10,
        authorized: bool = True,
        json_: bool = True,
        debug_key: Optional[str] = None,
    ) -> Union[str, List[Any], Dict[Any, Any]]:
        """
        The request function is used to make requests to the API.
        It takes in a method, end_point, headers (optional), params (optional), request_data (optional) and timeout(default 10 seconds).
        If authorized is True then it will add an Authorization header with the access token. If json is true then it will try to parse the response as JSON.

        :param self: Used to access the instance variables of the class.
        :param method:str: Used to specify the HTTP method.
        :param end_point:str: Used to determine the end point to which the request will be sent.
        :param headers:Optional[Dict[str: Used to set the headers of the request.
        :param Any]]=None: Used to make the function compatible with both Python 2 and 3.
        :param params:Optional[Dict[str: Used to indicate that the params parameter is optional.
        :param Any]]=None: Used to make the function return None if no data is returned.
        :param request_data:Optional[Dict[str: Used to send data to the server.
        :param Any]]=None: Used to make the function call compatible with both Python 2 and 3.
        :param timeout:int=10: Used to set the timeout for all requests.
        :param authorized:bool=True: Used to indicate that the request is authorized.
        :param json_:bool=True: Used to determine if the response should be returned as a JSON object or not.
        :param debug_key:Optional[str]=None: Used to debug the response of a request.
        :param : Used to determine if the response is a list or a dictionary.
        :return: a response object, which is a dictionary.

        :doc-author: Trelent
        """

        if headers is None:
            headers = {}

        if params is None:
            params = {}

        headers.update(self.DEFAULT_HEADERS)

        if authorized:
            if self.access_token is None:
                raise errors.AuthenticationError("Need token to make authorized requests")
            headers["Authorization"] = f"Bearer {self.access_token}"

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
            if response.status_code == 401:
                self.get_anonymous_access_token()

            if not self.access_token is None:
                if self.debug:
                    print(f"Connection error: {response.status_code}")
                    print(response.text)
                return self.request(method, end_point, headers, params, request_data, timeout, authorized, json_, debug_key)

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
        """
        The __init__ function is called when a class is instantiated.
        It initializes the attributes of the class, sets up any default behavior, and runs any other code necessary to do this.

        :param self: Used to access the instance of the class.
        :param debug:bool=False: Used to turn off debugging.
        :param debug_fn:Optional[str]=None: Used to specify a filename to be used to debug when the debug_value is True.
        :param debug_value:bool=True: Used to enable/disable the debug mode storing values in the file
        :return: None.

        :doc-author: Trelent
        """
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
        """
        Description of Categories

        Attributes:
            __client (type):

        Args:
            client (Client):

        """

        def __init__(self, client: Client) -> None:
            """
            The __init__ function is called when a new instance of the class is created.
            The __init__ function receives the arguments passed to the class constructor as its own arguments.
            In this case, we are receiving a reference to an object of type Client and storing it in our instance variable self._client.

            :param self: Used to distinguish the instance of the class being created.
            :param client:Client: Used to access the client object.
            :return: None.

            :doc-author: Trelent
            """
            self.__client = client
            self.data: Dict[Union[int, str], Client.Category] = {}

        def list(self):
            """
            The list function returns a list of all the categories in the system.

            :param self: Used to access the instance variables of the class.
            :return: a list of categories.

            :doc-author: Trelent
            """
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
            """
            The get function returns a category object based on the id or name.

            Parameters
            ----------
            id : int, optional
                The id of the category to return. If not specified, then name must be specified.  Default is None.
            name : str, optional
                The name of the category to return. If not specified, then id must be specified. Default is None.

            :param self: Used to access the instance of the class.
            :param id:Optional[int]=None: Used to indicate that the parameter is optional.
            :param name:Optional[str]=None: Used to indicate that the parameter is optional.
            :return: the Category object with the given id or name.

            :doc-author: Trelent
            """
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
        """
        Description of Products

        Attributes:
            __client (type):

        Args:
            client (Client):

        """

        def __init__(self, client: Client) -> None:
            """
            The __init__ function is called when a new instance of the class is created.
            The __init__ function receives the arguments passed to the class constructor as its own arguments.
            In this case, we are receiving a reference to an object of type Client and storing it in our instance variable self._client.

            :param self: Used to distinguish the instance of the class being created.
            :param client:Client: Used to access the client object.
            :return: None.

            :doc-author: Trelent
            """
            self.__client = client
            self.data: Dict[Union[int, str], Dict[int, Client.Product]] = {}

        @typing.overload
        def list(self) -> Dict[Union[int, str], Dict[int, Client.Product]]:
            ...

        @typing.overload
        def list(self, category: Client.Category) -> Dict[int, Client.Product]:
            ...

        def list(self, category: Optional[Client.Category] = None):
            """
            The list function is used to list all products in a given category.

            :param self: Used to access the instance of the class.
            :param category:Optional[Client.Category]=None: Used to specify the category to list.
            :return: a dictionary of lists containing the products.

            :doc-author: Trelent
            """
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
        """
        Description of Images

        Attributes:
            __client (type):

        Args:
            client (Client):

        """

        def __init__(self, client: Client) -> None:
            """
            The __init__ function is called when an instance of the class is created.
            It initializes all of the variables in a class and prepares them for use.

            :param self: Used to distinguish the instance of the class being created from other instances.
            :param client:Client: Used to connect to the server.
            :return: self.

            :doc-author: Trelent
            """
            self.__client = client

        def process(self, data: List[Dict[str, Any]]):
            """
            The process function is the main function of the class. It is responsible for taking in a list of dictionaries and
            returning a list of Image objects. The process function iterates through each dictionary, creates an Image object from
            each one, and appends it to a list which is then returned.

            :param self: Used to refer to the instance of the class.
            :param data:List[Dict[str: Used to pass the data to the process function.
            :param Any]]: Used to tell the type checker that it should.
            :return: a list of Image objects.

            :doc-author: Trelent
            """
            temp: List[Client.Image] = []
            for elem in data:
                temp.append(self.__client.Image(self.__client, data=elem))

            return temp

    class Product(Product):
        """
        Description of Product

        Attributes:
            __client (type):
            name (type):
            brand (type):
            shop_type (type):
            category (type):
            subcategory (type):
            nix18 (type):
            nutriscore (type):
            sample (type):
            sponsored (type):
            icons (type):
            stickers (type):
            description (type):
            description_html (type):
            description_extra (type):
            price_raw (type):
            price_current (type):
            unit_price_description (type):
            unit_size (type):
            order_availability (type):
            order_availability_description (type):
            available_online (type):
            orderable (type):
            bonus (type):
            bonus_price (type):
            bonus_infinite (type):
            bonus_start_date (type):
            bonus_end_date (type):
            bonus_type (type):
            bonus_mechanism (type):
            bonus_period_description (type):
            stapel_bonus (type):
            discount_type (type):
            segment_type (type):
            bonus_segment_id (type):
            bonus_segment_description (type):
            bundle (type):
            bundle_items (type):

        Inheritance:
            Product:

        Args:
            client (Client):
            id (Optional[int]=None,data:Optional[Dict[str,Any]]=None):

        """

        def __init__(self, client: Client, id: Optional[int] = None, data: Optional[Dict[str, Any]] = None) -> None:
            """
            The __init__ function is called when a new instance of the class is created.
            It initializes all the variables and does any setup work that is required to make
            the class work. In this case, it sets up the client variable which will be used by
            all other functions in this class.

            :param self: Used to distinguish between the class and instance methods.
            :param client:Client: Used to access the client's API.
            :param id:Optional[int]=None: Used to tell the constructor that we are creating a new object.
            :param data:Optional[Dict[str: Used to allow the class to be initilized without data.
            :param Any]]=None: Used to force the return type of a function to be Optional[Dict[str, Any]].
            :return: nothing.

            :doc-author: Trelent
            """
            self.__client = client

            if data is None and id is None:
                raise ValueError("When initilizing category need to have data or id")

            if not data is None:
                id = data.get("webshopId")

                if id is None:
                    raise ValueError("Expected data to have ID")

            super().__init__(id)

            if not data is None:
                images_data: List[Dict[str, Any]] = data.get("images", [])
                start_date_raw = data.get("bonusStartDate")
                end_date_raw = data.get("bonusEndDate")
                bonus_type_raw = data.get("promotionType")
                discount_type_raw = data.get("discountType")
                segment_type_raw = data.get("segmentType")

                self.name = data.get("title")
                self.brand = data.get("brand")
                self.shop_type = ShopType[data.get("shopType", "UNKNOWN")]
                self.category = data.get("mainCategory")
                self.subcategory = data.get("subCategory")
                self.nix18 = data.get("nix18", False)
                self.nutriscore = data.get("nutriscore")
                self.sample = data.get("isSample", False)
                self.sponsored = data.get("isSponsored", False)

                self.images: List[Client.Image] = self.__client.images.process(images_data)
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

        def details(self):
            response = self.__client.request("GET", f"mobile-services/product/detail/v4/fir/{self.id}", debug_key="product_details")

            if not isinstance(response, dict):
                raise ValueError("Expected value to be dict")

            data: Dict[str, Any] = response
            productCard: Dict[str, Any] = data.get("productCard", {})
            self.subcategory_id = productCard.get("subCategoryId")
            self.description_extra = "\n".join(productCard.get("extraDescriptions", []))

            properties: Dict[str, Any] = productCard.get("properties", {})

            self.fragrance = properties.get("da_fragrance", [])

            smaak: List[str] = properties.get("np_smaak", [])
            self.taste = properties.get("da_taste", [])
            self.taste.extend(smaak)

            kleur: List[str] = properties.get("np_kleur", [])
            self.colour = properties.get("da_colour", [])
            self.colour.extend(kleur)

            druivenras: List[str] = properties.get("np_druivenras", [])
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

            maturation: List[str] = properties.get("np_rijping", [])
            self.maturity = properties.get("da_maturity", [])
            self.maturity.extend(maturation)

            vetgehalte: List[str] = properties.get("np_vetgehalte", [])
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

            recommended_usage: List[str] = properties.get("da_recommended_usage", [])
            self.usage = properties.get("da_usage", [])
            self.usage.extend(recommended_usage)

            self.closure_method = properties.get("da_closure_method", [])
            self.tasty_with = properties.get("da_tasty_with", [])

            streek: List[str] = properties.get("np_streek", [])
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
                url = data.get("url")
                height = data.get("height")
                width = data.get("width")

            if url is None:
                raise ValueError("Expected image url not to be None")

            super().__init__(url, height, width)
