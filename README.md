# Supermarket-connector

![Supported Versions](https://img.shields.io/pypi/pyversions/supermarket-connector)
![Version](https://img.shields.io/pypi/v/supermarket-connector?label=package%20version)
![Downloads](https://img.shields.io/pypi/dm/supermarket-connector)
![Status](https://img.shields.io/pypi/status/supermarket-connector)
 
Simple api-clients for different supermarket mobile apis. 

```python

from supermarket_connector.nl.albert_heijn.client import Client

ah_client = Client()

ah_categories = ah_client.categories.list()

ah_products_category = ah_client.products.list(ah_categories[1234])

print(ah_products_category_1[20198].details())

```

This api-client allows you to access all data find within the mobile api of the supermarket. This can be used to check prices, promotions or for instance alergies.

## Installing

Supermarket-connector is available on PyPI:

```console
$ python -m pip install supermarket-connector
```

Supermarket-connector is build for python 3.9+.

## Current supermarkets connected

* Dutch
  * Albert Heijn
  * Jumbo
  * Picnic

## Features

* List all categories
* List sub-categories of category
* Find category based on id or name
* List all products
* List products by category
* Give details of product
