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
from supermarket_connector.models.image import Image
from supermarket_connector.models.product import Product


class Client:
    BASE_URL = "https://pls-sprmrkt-mw.prd.vdc1.plus.nl/api/v3/"
    DEFAULT_HEADERS = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "Supermarket-Connector", "Debug", "PLUS")
    AUTH_COOKIE_KEY = "reese84"

    AUTH_DICT_DATA = {
        "solution": {
            "interrogation": {
                "p": "IrfkY8S0oyIit0dzhSM0VhQjloaXNRU18iajItW1IsJGY7T0JCY0Vpcnp3UkdbIm5CNjVKMi1bXC14MidTcWdfQkxmMWNRX203Yi0yKj9tSWp8bG8hbiUwIDdYLmlvZGN3fkAgJFAxMD4gKzlnVj5rNDhwJDYwKSBxTGB3VWJlaWtPJHM1Pic2MzggKEtNRFwsTGAraWAlZWdLY2kvY0AieG1vbyVgMT4lPiA+IDAgMWNRZmlidT8nMzM+ICYwX08iUTkwPiQ+ITU+JjAxMCY1SClkaWR+b2NwJGRxPSIpIiwuRDRJeHlRX0NcbTlaMiViLS5jVVwiJDIpfklUT0h8YVFjUiZ7ejgyI0g5VVNHaWFHVFNkMmd6dX9pOHU3P0xlTTdiLTZqPGFlY3IsKTg2R0d2bTN6MiIrXmVlXSIjXX1SLC5JN19IdmFJenJxN1JHXWRKMilCIT5iU1dlQlZ3fW1HckphUTFEV1pyWERaTkMzaG5BNVxLZkJQPkReSkR5cWJAd09COGhTYWR9b0ppSWlJM25vST5EXU5FVkRqekI1VTJWUVhRMjRUNTA0XGlabklpQ0FTclRSX0ZVRFEyW21KTGA/QHlJaUk9TGNUOH1kY0pFVFpdRl5JaUlpU3E6dWVGWmVYbGdeSmk1QmxsZElcZlA+RkB2RWxgeFRodkM+TG5IQVlyUjFiWlM+R3JGU1B6W2ZbSkI0ZHFVV1E0fWNWX2pgWWpDUV9pM1VSXGMxbERjMVRKUjFeSUl5QTh5YWtodUNsRG5tRXQwM1hwcDlSQlVXXkJMaVtGRFRYaHAyU05AOldVO2RiUTVEUzd1Qll6TW9DWUlpSTVMYVk8bGlfSUNZQjh5YW5FXGRQMlE9SlUwM1F4Z1FuTGZUVTJQNGJfanBZakNQUlpFVFxtTG5JY3hCLTIsLkQ+Rjh1Y09KfmRHWGhdan5COTFWeDpIQjxtN2oyKFIgNlBZbkhTVXVUXUdyVkJVSkpla2VER1d2WmZXQkxiYHByNGpKQTdUfG1hYzxlXUlyREFWUHE2WFtkUWd7a2NSPkVSa2hnSllKWENSQHZDVH5LYW1OR1RVWGExa2xhNlRBPWVkV3dWWn5KYm9mRkRuTkVOTkZVWlJyVE1GUTAyaGRmQmlgfGlYRHVWV1JMYmBwcjNqRlRKWEh3QmtKTWVvZGZEbUpBN1RyXmdaVkdKU3hmRWFgdVpUWUlpQ3pdY2tpM0VgNldJQDN8aFN5Q1NTPkxkUFtqZVd4Z1dbbkdKX0RmRVxmSmNRelRRWk5CN1JxPWNqTGAzVTUwMm9GRkJUelxvQVxlVFB8YjJWTkI1YzRmQWhqW2pYQUhCZTpHUVI4ZVJhYHVUVExnRlppNUpZVHdBWlpRNVR8Yz1DeVExanh3RFJSWFRURlRRZkFSNlA+RFleSHdZWFU9YlFmQjZcSlxhYVk3U1FxSFJRMlIzU3U9YWloaERYVGhCY1B2V1A4ZlJoYldHWVxuZVtJUjxJakNKXWFIQmZ5PWRgdkdBamh3U2d1R0dZaHl5RGE6Ymp7a21BMkRCVVlVSll3aE1If2ZCUTpcYWFZN1NRdGhSY1B2VGB8YjNqQUpmV35FVlFlUT1FMHdOSkxralRId0NfYldBUjhlUmFgdVRUTGdGWmk1SllUd0FaWlE1VHxjPUN5UTFqeHdEUlJYVFRGVFFmQVI2UD5EWV5Id1lYVT1iUWZCNlxKXGFhWTdTUXFIUlEyUjNTdT1haWhoRFhUaEJjUHZXUDhmUmhiV0dZXG5lW0lSPElpQ0lIc3xoU3lDU1M+TGRQW2plV3hnV1tuR0pfRGZFXGZKY1F6VFFaTkI3UnE9Y2pMYDNVNTAyb0ZGQlR6XG9BXGVUUHxiMlZOQjVjNGZBaGpbalhBSEJlOkdRUjhlUmFgdVRUTGdGWmk1SllUd0FaWlE1VHxjPUN5UTFqeHdEUlJYVFRGVFFmQVI2UD5EWV5Id1lYVT1iUWZCNlxKXGFhWTdTUXFIUlEyUjNTdT1haWhoRFhUaEJjUHZXUDhmUmhiV0dZXG5lW0lSPElpQ0lHdHxiImIsI3QyT0h2YUl6MilCKmV3c05FM2J3Vj5kTUJfZVlRM2ltRHFMQUh7K2haaThfaGZnWFVROkFwczZAWXxiS0cxVlNZcTg2M31EXk5pTyZpZGNPRVlOaWsnempJcDJ1Vj5kQVNYZVJmU2I1Xm5MREJbJ0RReUhfaHZhMmVaSk9qQzA0WTlSSUcxWWtIMUg0OD1KbkB1TyVpdGprQ1A+Z2sndEJZfkJ4UW5iOVJSVVJmU2dRUXlMQUh7IDJpZThQckZgMFpbak9lMzlsSDFCS0cxWmtJfkg1OD1BNGF1PyVpZGtvQ15OZ29HfWJbJGJ3W05kXUpZRVJsY2NNR29sQUh7KWBUcDhQeHZiOFRZOk9gczpoWnhyS0JxW29Jfkg0PU1NYlV0byVjRGRfSllOamV3c05JfUJ1Vj5kTUJfZVlRM2lpUXhsQUJLJlhZY2hSeHZnWFRYekFwcztgWX5CSUxBXWNbJGg2PU1EXkB5TyZpZGNPQVduZ2sndE5If2J1Vj5pYVVmRVlcY2VVUXJcQ0JLJ1RVdVhfaHZpbENhSk9lMzpgVTVCS0cxWmtJcDg3OD1CNllmTyNpZGZRZlE+aG9HempJdHJ4Vj5oXUFfZVlRM2ltRHFcQUh7LGJgdkhRckZoVmlaWk9gcztkXy5CSkcxVEtJd3g0M31ETkF5TyZpZGRfRVpOaW9Hd1JYfGJ3Vj5oSVdaRVJmQ2AzamFcQUh7KWxDeUhReGZoVmNWSkJwczdSZTpCSUcxWEtJNlg0M31ISlhuTyNpZGMxZVU+Z2V3d1pYOUJ3UX5qaUNQNVJhM2RVWG1MQUh7IzBXYThRckZoQmNqSk9lMzE4WXBySUcxUDNaeGg3M31FSlhmTyVjRGxjU1N+aWV3dF5EOUJ4UX5jTUJfZVlRM2llUXNsREh7IDZhe2hReHZmXEJgekB1MzhSaypCSUJhXGFnOVg0OD1Lal5kbyRjRGdVaVZeamV3e2ZadTJ2W05kWUNXdVlcY2ptSmFMQUh7JFBReUhReGZtZFlWSk9qUzxgUzEySUJxUTFoOGg0M21KZlpmXyNpZGtrQmU+aW9HdFpJd3J1UX5kTUNbZVlRM2RdQXlMREhrJFBXakhfYkZhMmZmSkBwczZCaThiSUJhWmdadlg0M31LakJ1PyVjRGRbQ1d+Z2V3em5CO2J3Vj5qaUNQdVFsY2VFWGpMQkJbKnJkfkhSclZnSFlZSkF1MzhYVTpCTExBV19FM2g0ODItMiwtRjJDUklWYjNcbTg6MiwhNzItaTFiRWJSdGdZc1stMUItNHo1cnwlZTInRGFnNWJbaE1jV1E2Z2IrZmo8YWVjciwkZzdFaGlVRjhnZnYyU1suY3Q/YDsiM0ptaGhXeVllYVZCcVVaMiV+bGxiLCRoO0siQWYxY0hrI0FUUXJhQj09OjIidHVlciwkaDc/QkVnRjl3ZnNKMiVyK25vbm5nfCInMiNDYmFSMk5kTURSLTIqOWdTPmIiMiwkdztDV2VbQWJIaTY4aF9nOjIlcitub25uZ3wiJzIjQ2VkSXJHbU03ci0yKjhjT2J1bWBQJkRGUCVpZWd6MnBaMn9hZHxiYCVvZEVzZW1kfmZAIn9hbWo0cWowcHlsYWNpZH5vYH8mZGB+dmRkfCh1byR0YH52ZGB7NmhjT2J5bW1lcFAmREZQJWllZ3oycFoyf2FkfGJgJW9kRXNlbWR+ZkAif2FtajRxajBweWxhY2lkfm9gfyZkYH52ZGR8KHVvJHRgfnZkYHs2aW1Cc2N/Zm9gJHRlRWdgUCZERlAlaWVnejJwWjJ/YWR8YmAlb2RFc2VtZH5mQCJ/YW1qNHFqMHB5bGFjaWR+b2B/JmRgfnZkZHwodW8kdGB+dmRgezZkQFAmSWZXdWJ1ajo/YFRycmFlbGRAI29tZX5lYCR/Zk1idHFqOjBxbGBzaWRxb2lvLmRgfnZkYHwmZWR0eHB/JmRgfnZkZ1syZWlrQCR1cmxpbSR+aWBQJkRKOj9gVHJyYWVsZEAjb21lfmVgJH9mTWJ0cWo6MHFsYHNpZHFvaW8uZGB+dmRgfCZlZHR4cH8mZGB+dmRsIicyI0NlZElyQn1LSnFVNFJSLyt6NDImPklSQjNIYkljQ1h2clA1V25CI3IqMW5lbWlEZWRyLWIsJGk6TWJBZjlzXmUzSjIpYiVkci1iLC1FN1tHcWFHSXJ5PWhhXWRKMiJyJmVlYnhjfXIiLC5EM19HeVVHSjIkQiQ9bGxoT0RVZTVkQXVSY0lgdkg2TkFIcWhhU2tPSkpvbEduTyJ2QW5lTWZdZUsmYDQzb0Y7LWU8R29nNkEzODVcamFLa0hFYkM4d0FJQTQ1RWxESFU2aUdyQXdEeGZGOXUzUTdyQ1lXMFk6cHhSSFpRaGBSQ3hKWDAzc0F4NWRlMzRWfmlHNjVoO2V1OTdORFFhRkJuZ2lJTUtnc2llYUJ+RWdIVVlSVjRiWXBSSWU9QkMyRVIzY3IwV2lJMjNYVUtoUkpiXUZad21CaGZ3ZXVDeDgyMVZHY3JHSEpjPmlTO0A8QndyRVdpSyJZU3kyLTIsLUU3NWhyY0Y6MiVSJlA/QFJTMWV2WFVmZldCa2xtZGZlN0JsZldaU3k2UlRYNVpXOHdTYHE3SVZ5MTpZcldRaG5IQmZmV0JjdkdJWXJIVVZoa29MSkA1WE5OZlZoZk9GTkIzYHk3RGl5N0FqdTdYWGpDNGxod0pQeTxjbGZeZWA2V0hQMlEyWVR0VGpkZ0hZdTIxZn5IWlp6SFJneTdYWmZSNGlyWFpUMlhWVmhmT0ZOQjNgOkdCZmk9Y2B+QzNsYk5iZH5COlZqSFRhOGhEbGk2R1VVVUpXOTdIU3ZSNGlyWFpUMlhTZmZdaVtoZ1haclEyWVR0VG9iSEpcaTZJXmpIWF1iUTJZVHRSa2ZdaVN5PGlQOTdaU3k8Z1VVVUVnOkhUbGZIU2ZmXWFkclhUZmU3QmBwcjFqcldWVmhmT0ZCUzJoaHI4XWpSOVN4Z1NmZl1qXWZeaFlqQzJmeTdIWmJRMllUdFlUMTdRZXE3WlZlN0JsakdGVmhmT0ZOQzlVOkhZWXk2WltuR1lVclhSanxtYlZodVRYRUtvSWlJYFk0Z1RiXG1iZTh7ZVhGV1ZTQVI5Qnd5YWlgfGZfYH5tTkxlVFVCVFFubGZaVTxiMmpQdURYTG1mW0Q1RVdwd1FvSltkVHB3Ul9GR0ZWNGZUb0ZQN1F2SmJSRUdBV3JVVWhgNV9JakliZUQ1WUM0fmlJO2ltSHFVUlpxQ01DeDZIUT5DOUdyRE5GaTZUanFJbUhxVVRqfkdDbGxtaUVBRE5KcklpWnxiM29mR0JZcklzVUFDRVB4aWpTclhTVXFDUmN2V0JgO2tpT2ZVQl1FMDlCT2pgWWA1XUZ9QzRXekpkYThuZGpuRlJkRGZBVHxsZldHanlDN3lrSWh3VGxlN0tKQUNJVXUyOUpGV0pTeTIyVnlJeUYzamRnckREYThuY2puRlJkRGZBVHxsZldHanlDN3ltR39qcFlhNFJSWUVEWHB1RGI8ZlxHSlE9RnZSM2VQcD5CXUM2UzRjM2N1SmNUMHIyam5KeVEzan1Cc2E0V3pKZlF4aERqZHlhZExlQVxqTWlVS2RZRDd5bUh/anBZYTRSUzpANFdQdURiPGZcR0pRPUZ2UjNlUHA+Ql1DNlM0YzNjdUpjVDByMmpuSnlRM2p9QnNhNFd6SmZReGhEamR5YWRMZUFcak1pVUtkWUQ3eW9HeklmUj5IRVtEZF5KdGEyYzlIT0h0dUlReDI0an1HW0M+Sn1IVDVBaXJcaVQ5UzFSeGI6WkpFUlllR09FOUNNQ31ESUYwOmFZOkRWV0U1RFhId0NdRldUWHZFQ2ByVEJjNGpzXkh1VFF2SmNXRlVaWHR3UWtKUjZScHI2W2NzRlpySn1PQH1lZV5HS0I+QDNfZldZU0Jbb0hnZFxJZURPSnlJYFk1RVZXclZCX0hwNFN8ZUNsaHVRYkFIVGA4MjRTPGVRbUQ7Ylh8a2NmRldTUnR9YW1kYTpRcVZNQnNhNFd6SmZReGhEamR5YWRMZUFcak1pVUtkWUQ3eW9HekljYHJUQmM0anNeSHVUUXZKY1dGVVpYdHdRa0pSNlJwcjZbY3NGWnJKfU9AfWVlXkdLQj5AM19mV1lTQltvSGdkXElhRE9KeUliaTZSNWVKW2NZelxjVFhlV1RVWmRqdGpjX0ZHWlVUc0RSWGVUaXZMZGZ6R1JWcHIxalN5ZlpySn1PQH1lZV5HS0I+QDNfZldZU0Jbb0hnZFxJZURPSnlJY1k0c1VoSltjWXpcY1RYZVdUVVpkanRqY19GR1pVVHNEUlhlVGl2TGRmekdSVnByMWpTeWZackp9T0B9ZWVeR0tCPkAzX2ZXWVNCW29IZ2RcSWFESUYwOmRpPkp+QjUwOVpCVltLZkEzXkpIRVI5N1lROT1haExsa0F+Sn1IVDVBaXJcaVQ5UzFSeGI6WkpFUlllR09FOUNNQ31ESUYxOmNSWHAxU1xhMW1FO2RmdGIzYVpQNFJRWEJQM3I0Z3huZ1pEd1VQMTdTUHRkRGthMjNqclpyUjpFT0NaVFpUNkA0aHpSOVJQNVlBN3ltSH9qcFlsZVRdQHZHVEh1VFF5PWpTMkEyWnZMZG1CVEFoQkp1YjxlQWpSUzJiXGdeSUJSMmM+SF5KelhBVUlMbkU4bmFeZkhaUzZMZFhlVFxJYURJRjA6ZGkwcDRSUVhCUDNyNGd4bmdaRHdVUDE3U1B0ZERrYTIzanJaclI6RU9DWlRaVDZANGh6UjlSUDVZQTd5bUd/anBZaTdSXGB4Q2dAe2VXXGA1WU9hPUE5UzRTPGtmWGFXRVJxNVNpSl5iYlZTOlloYTZQcHdUYF5DM2pyWnJSOkVPQ1pUWlQ2QDRoelI5UlA1WUE3eW1If2pwWWtlUlJwczNnQHtlV1xgNVlPYT1BOVM0UzxrZlhhV0VScTVTaUpeYmJWUzpZaGE2UHB3VGBeQzNqclpyUjpFT0NaVFpUNkA0aHpSOVJQNVlBN3lvR3lJYFkzaFRqdGpjX0ZHWlVUc0RSWGVUaXZMZGZ6R1debGdBZlk7Y2M+Qz5KelhBVUlMbkU4bmFeZkhaUzZMZFhlVFxJYURPSnpJZV9GTmpZQ3VCUD5Obkd0ZERWOGRDW0JRPk9NTWZQNl5hXGJUUlB8YDFnWGxqVXhoU25tQzRgMltlU0tqZWI0Z0NiRGhVXWZHXk5JQ11DfURZRjpbY2tIa2NbYlpzZ0FDPkAwcz9NQHVGXEQ1SVIyWnRnVldeQkxnQ1hKVldRdTdFbGRnQ2pyWnJSOkVPQ1pUWlQ2QDRoelI5UlA1WUE3eW9HeUljWThkU1tCUT5PTU1mUDZeYVxiVFJQfGAxZ1hsalV4aFNubUM0YDJbZVNLamViNGdDYkRoVV1mR15OSUNeQ3lKf0h6SWlXSTtjV0Q7ZFA4Zk5MZlVUYXlHRGlyVlRafUI/QzRzWllGSnRuZVVaUTZSPUZ2Uz5KY3l2WnJKfU9AfWVlXkdLQj5AM19mV1lTQltvSGdkXEljZE1Jf2RWWWpHQ1BQdU5PSHVKWVZUUWZCXm1JZl5jZVkwPkpranNSc2dKWHZTPkZEZ1Jsbkp5UTNqfUJzYTRXekpmUXhoRGpkeWFkTGVBXGpNaVVLZFlEN3ltSn9qYFlpN11KVl5jZVkwPkpranNSc2dKWHZTPkZEZ1Jsbkp5UTNqfUJzYTRXekpmUXhoRGpkeWFkTGVBXGpNaVVLZFlEN3ltQzVKaUYxO2FpRlplYlk7ZFZAe2NZfkVDWHdlXUJxVFJneTl0X0A3Q2p6WnFTQkRaWnxmUWtKUjZScHI2W2NzRlpySn1PQH1lZV5HS0I+QDNfZldZU0Jbb0hnZFxJY2RNSX9kUllqV15AdkZUVjZQM19KTmFZRkMzWkNzTkhyRExGdTAybU5EXkp6S21CTkhHXGB1WlJ0fWFoUl1rRV5KfUhUNUFpclxpVDlTMVJ4YjpaSkVSWWVHT0U5Q01DeUp5RjE6Y1Z3ZV1CcVRSZ3k5dF9AN0NqelpxU0JEWlp8ZlFrSlI2UnByNltjc0Zackp9T0B9ZWVeR0tCPkAzX2ZXWVNCW29IZ2RcSWNkTUl/ZFBZYTRdQkpbZFVUa2JtSHVKWkZIUV1MZ15HdGhORnEwNFpAd01PSVVSV3ZIX0AySEZROTdRaExsa0F+Sn1IVDVBaXJcaVQ5UzFSeGI6WkpFUlllR09FOUNOQ3lKf0h5SWBZNUVWV3JWQl9IcDRTfGVDbGh1UWJBSFRgODI0UzxlUW1EO2JYckpjZkFYU2Q2WEJmVGA3UX9nXUJzYTRXekpmUXhoRGpkeWFkTGVBXGpNaVVLZFlEN3ltSn9qYWlhSFRgODI0UzxlUW1EO2JYckpjZkFYU2Q2WEJmVGA3UX9nXUJzYTRXekpmUXhoRGpkeWFkTGVBXGpNaVVLZFlEN3ltQzVKaUYwOmVZMlVdQ0h1VGtGXmJaWTliZ15KdlxuSEVbRGReSnRhMmM5SE9IdkhGUH5IQWhHZVpTNGhDZH1DNGAyW2VTS2plYjRnQ2JEaFVdZkdeTklDXkN5Sn9IeUlgWTRoUVhKXGNdSl5nUTlVVlZ4PWpaclZTWnVMY2M0anRoWHI9SXhkUWhyVlJafGI+SUJSMmM+SF5KelhBVUlMbkU4bmFeZkhaUzZMZFhlVFxJbURPSXpJZlI+SEVbRGReSnRhMmM5SE9IdkhGUH5IQWhHZVpTNGhDZH1DNGAyW2VTS2plYjRnQ2JEaFVdZkdeTklDXkN5Sn9IeUlgWTVFUllyXGJfSHA0U3xlQ2xodVFiQUhUYDgyNFM8ZVFtRDtiWHJKY2ZBWFNkNlhKVlhhNlBwd1RgXkMzanJaclI6RU9DWlRaVDZANGh6UjlSUDVZQTd5bUM1SmlGMDphWTJEVlVVNURYSHdDXUZXVFh2RUNgclRCYzRqc15IdVRRdkptR0ZVRGh4ZERndlZXXmxnQWZZO2NjPkM+SnpYQVVJTG5FOG5hXmZIWlM2TGRYZVRcSW1ET0l6SWNgclRCYzRqc15IdVRRdkptR0ZVRGh4ZERndlZXXmxnQWZZO2NjPkM+SnpYQVVJTG5FOG5hXmZIWlM2TGRYZVRcSWNkTUl/ZFBZaTdSXGB4Q2dAe2VXXGA1WU9hPUE5UzRTPGtmWGFXRVJxNVNpRG1nUlxnU1tod1deZTdFbGRnQ2pyWnJSOkVPQ1pUWlQ2QDRoelI5UlA1WUE3eW1DNUppRjE6a0pEYDJWOk5mW05MY1pORk5BbkReQjUwOVpCVltLZkEzXkpIRV5sZlpQfGVKU3hhOlV4aFNubUM0YDJbZVNLamViNGdDYkRoVV1mR15OSUNdQ3lKeUYwOmRpPkp+QjUwOVpCVltLZkEzXkpIRV5sZlpQfGVKU3hhOlV4aFNubUM0YDJbZVNLamViNGdDYkRoVV1mR15OSUNZQ3xpZGR8Z1JkekMxX2FJfEd5SmVXZVA0V2RlSlVySFtAUUNMR3VKZFdkZUpZY2ZfSWlJYFk0Z1RVekRaVDhsZFhlVFxJakNBYDR1WlljZl9JaklhXERjMVpWR15OSUNdQ39kTElqQjZeZURFaXpIVGhKRVNYaTA/SmlDWUN8aWRkfGdSZHpDMV9hSXxHdUplV2VQNFduRkJdQklyVFJDUl1FMjNsaDVJT2FETUVyQ1JUUkNVXUhwOUhIdUlYRl1pSF9qZGliVFJnekdCbmh3WlI6XmNlNGM9TkhyMV1FTGlVPGhUWXxoWVNGS2lQWVp8SWpDQl1KQjZcYklxYDR1WlljZl9JaUllWTxnUV5uRVdTNkVUXEVUXElnZElGMTplZlRtZGlKRl5IZHA+TklDWFNzZF5COUp8SnNkTkI5Sndaf2pwWWxlVWFUd0paWURTUTZFRWleTGFlMlZFUTFdbUM0O2lAN3lvQjFEX0A5SW5JNkRNSXhkWltKQTJqRHdFZER5YmU+R11PRlZVVU5GVFJyUDZfZldKU1NkRFlxWmxJaVRPSHpJbk9NQjlRMTAzaVE3U1ZcbWNVWlZRUXJRPUxoampTOGhDVlZGQWRZMDFlQlZFXGFdbUM0O2lAN3ltQj9kVVlncD1Gc2I5V3xjNlZaRkFkWTAxZUJWRVxhXW1DNDtpQDd5bUd/anBZYTRSYzpXRGFfbm9FMDVDaXpDNVRcbmZQXGdEVVpBPktqSn5PSUNOQ3dkTkp1SmlGMDpkaTZKcmpwMDRoekhWVFZTMlR4Z0pTWkZeS2pKfk9JQ05DdUppRjE6Y15Ad1pYRTI2UHRqZW9GXmRSQkpjYT5MZGhRN1FlSkZFXGFdbUM0O2lAN3lvQD1ETUI/ZFBZYTRSYzdsZ1Awd05ETGpzZTNjPUQ2XGVdbkxrQT5AN1N2V0pTU2REWXFabElhVE1JdURJRjA6ZVk0c1pYRkpxanEwNGd1VVdUPGdOSFR5elM8YTVgWHdVWUVGUVE8YzJTfkVKUlNkRFlxWmxJYVRNRDlaf0h5SWBZNkZSYTkyNGZ5RVdUNGdGVkJGRWU8ZkVsZkhUaV5CNFQ+QTJTdlI6UlNkRFlxWmxJaURPSnlJYWkyUzdQUlZNT0ZFVlp2WFJackhZUThqallWUDVVXGhHVDZXVGU4ZVVTXG5hZTR3XUhKTG5Lakp+T0lDTkN1SmlGMTpkUndoU2E4bmJiXGI6VTZQNVUxXW1DNDtpQDd5b0Q5SWBZNkVUaFk7YmRXdVFZdkI6U0tkWUQ3eW1AP2pgWWE0VlJKUzVQUTI9T05MZV1uRl5PSUNfQ39kRGlsbWFkSlRBVEZdY1NBUjlDOHlkbGpIX0A6SWRTeGhNSVxnUWRVUDVSNl1iX0tqeUM3eW9EOUlgWTZFVGhZO2JkVVVVWXpSMl5BUjlDOHluRGlETUd3c1dYf2pyaWZWUWtOR0JqSHdGXEVYSlpySn5KfGdBUjhsZlY8YzZZdlI3U0pbalhDZExJYDZMSHZET0JqSWZUcHVZX2xgMmN2VURVeGM3UDZYUmUyVUVTRkRVaFpIWlhaRVJRZGtuS2lJeUN0bmNoYl1hZmJYVGNxN1RWZGVCU0NmVGc4aERsZTdJVnkxM2xpMjhTeHAxWEZbb0heQzpZeldUbWpHVGZmQjpZeTZCXUpANlZEenNsZl5lYDZXSFA4YjNgNldIW2hwMVhGW29IXkM6WXJXUWhuSEpWZlM6WWJXVFZkZUJTQ2ZSZzpSMWV5NlpZekhaXGU3Q2xpPGRuakdaXGk2Ql1KQDZWRHp6WWpDOFp+Qj1APkM6VmpIVGE4aERsaTZKW25IWlp6SFJneTdYWmhwMVhGW29IXkI9QD5DOlZqSFRhOGhEbGk2SltuSFpaekhSZ3k3WFpocDFYRltvSFJTMmhocjhdakM6XGpdaVE5PGJpeHI5VnkxMl1KQDZWRHp5UDZSOVF5PWVmZkdTaXZNZWZmV0NgNl1oUj5BNFZEenlZdldRZXh3VGZmR0JmeldKVmh9YWhpNkNsZl5lYDZXSFA+QTRWRHp5UDk3WlN5PGJtZkdIX2ZSNGlyWFpUMlhVVmZQP0BaQzpYZTdSYHk2SVA5N1pTeTxjbGZeZWA2V0hQPkE0VkR6eVA5N1pTeTxjbGZeZWA2V0hQPkE0VkR6elp6WFRgdkdBYjpIWlxpNkNrZk1ia2ZNY2A5MTJUWDVTZzZHQ2R8Z0hUekM6XGU3Q2xpPGlWel1iJmIsLUU3NWhyY0YyXm9mMlNdMVoyIit+RTc1YlVmX0RbZT9CUV8kQ3Q/Y3sndGRaMidiJHVhYFFidW1lZHIiciwuRTc1YlVmX0RbZT9CUV8kQ3Q/Y3sndUpoV20zejIidHVlfC13MiNTdWhPYkItMioxVnFwckdEWEAxOHFEdXNHSFl8RURJYWJdamJkUz1hY2RBUjNUYVk0Ujh8TEM5RjBURUNBczRqVTZnbEtiaHdjdzJFUHc6R0ZDND5Cf0tDQDtFSUN3SyFBPGB3WlpnSGVSRlE4SDdLKTNcYDlBWEFiWUlxUldBXEJEY2F2ZXU1Z3Y5QnU6aU1Id0h8aXFMZVkyMzY1fkdqYHFIMjdlfEZPIVNpaWxCM1pmeFsjUTFiWDdKeXhANzZ0NDl5OkFGOVRpZF9mQFZZT2NkNlJodkBVNEN0QnFGTT08IiYyIW1BYkAyUi0yKjlnczlBeURRYkk0WFl0ZFxBeU5tSXJCMmhqSFFjeHlpSXVXWkNBO2FjMDljaXA6a0d6TWNpaTdZWDxoUmlpQztBMlVOQXN5bUlyQjxIek1pWWh4UWwiKTInTkFuQDJSLTIqNThyOFA2cDl9a2lHa2RqWkJ5cHgySWZbQFxoRmlHZ1N3OWhIX2k4MmVXSXJCZjVTN3JSfWgxZHl/IHFTTkpXeUp8Qn5ITkZJSmk4NTpMbUZsQ0RGSndRbylFeXdqSGIyQTpGM0E+SHg1dDp2RHNIaTRpPyhgPGNhYHhAX2pER1pAcHxnWlQ+aGRYQVhWYTshV2pjV0FTRUhlelJ8YDZ5SWlmVURYSlNKTW9GZWRuTGNGWHsiOlVKSUwiJTIhbUlRQ0dyK0IqP2dHb2VsaUAjbmIuIiwoODFDSGlRV0FIbT06MidCI2Vva2wiKDIjSDlRR0hicVdaeFBzaHItMiowMjMwMTA3MDwiKDIrSTlUVWhnZ103Yi0yKjI3V0REQHJzMXVTWGpGMlM3cFVvSnFRRVNobERUYlxiYHFSQXVYc0hvKT9CUHhnRn1qZkV1VGBxb2xMQUc6aU9DaGVVaXVaRGBwPW9JaTVAdmB4NVNpbGJ1eyBXUlpQUm5Da2slRGJhYXstQ3Z6emdVX2BxbUVZSElpUDZlSlpHZ3RUWDNANWMwODZVUj5FTWZBe2ZiVVAzSG1gWExsRXBRSURuZ3dBaUd2dXVNSHJ8YX5JV3BZXy1rKTlSVThiNWg1Mk9nP2RNRHpuaT9rKFFZZXVUNkJrSkZFWENdT0BUUjFUMnpCcnM6WX8lSDJpV3hhVURNRUNEZnRfK01lRTtJeGVGNjBRdHZ7I31CdFVicmRiRT9IUlhXWXdYXyhKQnY2OEpPSXI6WGRkNm9JVzNeYFxnRVUwd3R9SURWUzNofmFrIXR1TUZhe2ZJUDVCfEdFQWFyd2pBbyNhfURUN0lVMlsrR0FZZER5a0NxODhnVlZ1UmVad0phZTE1anp6YldKdWYyeEZiZz9kTydBR3JzWXpFOEtiWVlIRFRGdGAzOl1jTEFSdG9ndm5lZ3dwXGh6UUN0dDc8YzZ6WTh0cDU1TGskYVpkND1MREc/Qkd1OnBUP05KcT1HOlxmcjRNakVIVFlYRXJnaHpxZnVzbkZFUmR5VEc2ZUQ8T21rSD5lREN3S2NyOytEczhCdVcxVTg2MXQ7RlV8ZXE/RXFnUTdLLmdnOylcRDh/JHdoYDQ2TGdMY2h1cFRSb0FYNVpXT2Nmc0U5RzZJc1pUN2M7JEJZYzxBOFdoN1A3YVVnNlJbS2JUZEh0ZVhIRVpFRmV0c11HNU9FNWpGY0hKV3E0czJ/KUhdQkFTSDVCWD5tQ2slSmQxNkg6ZzNGZTRoSDJ6aVM3YXRjMjp/LGhfIWxFdDsjR1g0dkslUjpaQnsgPENrbkBSPkNGZjFyZHxEckc+am5oU3U1djh0S2tIaThHe2RfZX5JdEdLLkI3UF1uRTlKQjVDcnN0b2k7Jn5mZEpQXGRFemg4cUBZQUJhY1Y2Z0AySEZGPkBwcnhNQDRVOVN1RH8gXURxPmJyU0heQHpvZHBdQUJBWmdxY1JUcHNQVEgye2ByT29BeGFoQ1xpTUI6fUpoPWRvayFYZV8jMVVpYjZUSElZRW8rIWJsaHdYMTJkeGRnYFNgUkVTU3smdnBaVnk4YDlHcX9CMmE3MTdzZ0J8ZG8pNFxsZWpRWTZAODZ8QXJfSlM2SktmYHJrTGFRanlScFpyPEshfmp5b2N0WVVxQk5GMDpRNzJENW5rJjBRdjhnVz5BTGNxNGN2Y2R5QlFVOGJPREp5PUlwXGZiOUtOSVJ7ImNhVjRJVzkyVThiYWV3alVRQTZSSD1nUFZgVltkOlZLZF5BdDZyMDJ8TmFiMXdFXytFZUI7Z0VIeDBSWHladUZDYlVVWEpfJlI0c3A0TkshZTtPIXM2cDh7YUhKeUVZMmFdSEM+QVF/Z1kyeVlDMHVFf21sbWM8ZzVlXkJ0VDFXczNpQX5GZn9AWVRgfy1uaDN+Yj1nZH5CRDxnMD1kPkNkSml2SElAUzJafGNLZGJ2QDFNRnZLQ1J3R21EaFZKT0NAUHJ3NHdUM1FjM2ZhUmV8RUwiJjIlbUlRR1dyK0IqOWd3TEV5QjJjMlM5WWZCO0N5R1lCcT5pWWd3XEhpR1padldUaDpJaUllPmpOZkdRaHJSMmlsbWxDeUdZSyJHUWtpSWNsZ35pWmk+Y2E2UjlTUThcSXEzO0dFNl1ObG1qVER+Y1E6R19CSkdIVEh0WVdwOm9DeUppSXFXW0dFNVlZSTdGZm5GQlZ+TmpFOGI1ZXk6cV8jaXtNZTRGU1RkXEY3aW1Ad3ReTkpYQWB6V1JZf2dZSmpXRmxndEpSeUtkWGZQNVpWRVlYcDllUDA6ZWl2U0ZuZlltRUk2VWdYaE9HOkExWnxkVlJCVEJQMkhOTyRmSlljd0pBeUdeTGJdY25pSWlbZ3p0ZmhoQ1JsamJZfGRUYl5BMVAySEJfIVRKXmN1VG9gcjZacDplaWlIRGxmWWNld3RCVTNnQWhqWFdTbk5qWVRmQWlpNVZhOUM9RDZWX0hCUjNUelIyVHxkUFl/Z1lKaldGbGd0SlB5S2JualAwVXhgOlp5QjFQPkhHVjxiOV5iUjVjMDlpUjA6YWhod1pZfkNMQzJafkQ5VlVgWHZCXGExPk5oZlZZUkRNQztoVGYwenZYOURSa0E5bUJhOWVUd3RSVFhjMlR6UDJTYlIyaFRmWVkwOm9DeURZSXVROUpBNlZSTkIyVER3U1N5RElZf2NMRkEwPUhOTWRkRHExVnR4W0hsaFZVOkp9RT5OZlp9TWJTcTRSYXRpbUJ5RVZhO2A4V1ZAMWVOR0hYQltlVl5OZGY3YTRncURVW0ZWQWlkZEFZf2lpQ2R3WlxhPWJpZlhKQ3lOakV2V1pbaUljYHd9all+Q1ZrIldRZ3ZZY2lyU0xDdkI6WnpHVGtgMjZrbk1mbGU9algyWFpZMkdbS2ZNZmlnd0xAeUdTbyZTUmQyUzlQelhKXCInMil0cmZFeG5iVDliLTt6ODIjSDlRV0hua0QzQi0yKjR4YHR6M31yIiwkdzFRaXlXUjlnaTNHaF03ejIiK1FjSWxicmIpYiwlY0R+YnVyKXIsIWhEdWVkc35oY2VnfGlidWwiLUIicWVsZHR8IiBSKWJ0c35pYiFsLVQyL0N2bkFnd2ZdN3ItO3o4Mi9IMmc3SG1nX0RYX2JiSXVZXkd5PTdyLTE6MiwpNz5NYllcRWh3ZXY3dFloU3Q9YDV6dk8hS209OjIsIDcyI1RyYlVoaGlLI0NlNEhyPmFeR3k9N3ItO1o8LVUyKW5CYU0xQi07WjIrcnNyI2IqNHhgdHozfy8sYH0jcHN9YntifSR3fWB+JGJ2fiNkbiE8YHN1fm4vLGV0TSVncWlxYW0lYnZNJ2lkeGJNLmFtIXhkVX9oZ2R9JWhidW0lYnBZcWJ1bSN+b01yLC1XMitEcWRtMVItO1o9fVIsKTc+R1h1aFIzXml7IVNdNUoyKUImYntlVVE2QDlXVkVYWmJXRlRIYj9FVTVPRERkWlA8Yz1IXGpzWWkyM2xsZFlcRkM4UTNlVFY+SXJUeHRNS0ZJaV1oczpDe2dZSXEwOldGRlhYZkdFVEhhM1VUZU5KZGRCWytjPkM0Z0hQeGI6WVRoTUExOFRUc21iaXJVQlI4N0NrbURRYDhsZWRMaFpDWldQUXZHSVxpQzpDd2hBVzRoVlB0ampbTGI1UzpMZWRVPmRpR2plYTZUQWF4dUFeZkRCaEA0XUY4eWtDUl5sQjZQNVgxRElZclRCW0JGRV1BS2NhMURaUzJKZGR4eF1BWURAV35FQWRYemlVWkljaTItMiwkdzRJd3lWN1luanljQ1gyeDp1O2Z3dlBYWmJLYUdtPToyJWImY0pYakgzR1JYfkh7ayB4SVZeSnpGcWhHU0ZGNkR/SEJqWThJam9KcFczdGNiMTxqUTZBZkF0N0JiWkg6bmQ3QmZeQ0RxU2hGY1ZQdVF9R1JpMll4Z0V3Um1mQlxqaHhZWDJUM3pzMDpWZT5kZHdYRWlpOGhFfydKXUZUNUV3fm1Cc3xHQzY6d1NSXG1EWDA2V2ZfYHJwN1NjXkU2bU9COV9FNzE0eldSanJYUXE/Z1JmZThpdnVlUmRGWGpDc0VUaXpIfmsgcjNjVlp6QFFuYWZFNjZEf0hAUmN4SWp/SnRfKlRkbWE9ZGp+QWVBdD5iZlZYOm5kPWRUVkNGd2NtZmdWQHVRfUM4WXZZem1lfWJrZlJbamh+aVU1NDR6YzIyVFk+ZmR3XWVrZlhnRX8oRGVJRDZLJ3VNQnN8R0M2OnNUZlxuSmg3SlB2T29icDEzZVpFNGg/R1lSQTcwNHpVVmEyWFF8b2dSZmJYaHBVZ1ZkQlhrSDNHWlsmSHxlcHhJWlk6fEZxbWNfSTY2RH9HQmZTeElqf0pwVzRkZGdRN1pZclFlQWQ+YmJVODduZDM2YVkzQ3djbmZlWkB3W01HUmA8aXdtZX5ibG5CXGpoeElVOTQ2emM9alJYfmNkd1E1a2pIZksvJ1pSQTQ3RXd6fUJzfEZDNjExZlpMbkpoNkRpZk9icnA9Y2RSRTZoP0IzY0JXMTk6VUJoclhfYT9nUmhaSGd/JWdSbkJYak1DSFRneHh8ZXB3U2leSnpGYWhFY0ZWNUR/R1JkY3hJan9KcFc2RGRnQThUYDhhZkF0N1JlYlg5YzQ3UmRWQ0R3Y2hCZmpAdVY9RVZqfkl4YjV3VmliUl1qeHdZXyU0M3pjPGpWXk5jaTdYQWZ1OGVFfyM6VkN0N0snen1CdkxGSEY4VWVYbG5KaDdaVXJfYXcwN1lUVkU0Y39ISVBaRzA5OlVWYDJYUHE/Z1ZkUlhnfyVnVmVMaGxDc0I6WypIfGVgd1NkUkp8TyFiMW9ORjZJP0dQUmN4SWp/SnRZeHRkbWE4WlEyUWhGNDIyZmJYOWM0N0RUWGNDd2NnVmNWQHVRfUI2YDZZd21lfmJgfkJcanh4SVU+RDN6YzZEY1k+Y2R3WEFsakhmSy8oSlpGVDVFd3M9QnN8R0M2OnNTWHxuSmg4WlxiX2J3MDI5VmJVNWg/R0VTRlczNHpXUm8iWFBxP2dUWFZIaHBVZkhVTkhrTUNHSlh6SHtrIHdZVFJaek8hZ1VjTGY1RH9DNmVcaEdqb0IwVzN0ZWIxOnJZekFoRjQyNmheSDhjNDdWY15DQ3FDZ1ZhUlB2Vj1IVml2WXptZXVSbGJSXWpod1lYfkQ0dFM4RGNWXmNkd1dRZHJYZUVvLmpSTkQ3RXdyPUJzfEdDNjp3UVpMbkp4N1RqZl9icnA9Y2VWRTRjf0hJWkk3MzR6XWRaeThSfG9tYmVmWGd2dWI2ZUxobENzQjpbJkh8b0B+aVJcanxGcWdBYkpGOER/R0JmVlhIZE9OYmE1NGRtYThORzNxZ0Y0OnhRWkg4YzQ3VmRWU0Z3Y21mZVZAdlF9SEJlOTl6bWV9ZFppMl5qaH1pWyZUM3pjMjRlXG5mZHdSMWV+SGhPTydKUF5ENksnd1FcalxGQzY3UWViXG9KeDp+QnN/YHcwNlVUWkU1bU9FU2RJNzA0elIyZDpIUnE/YjJlaThodnVoVmRMaGxNQ01mUDpIe2sgd1lVbkp6TyFtYWZKRjVJP0ZCYl5ISWpvQjJhMlRlYjE6fkczcWZGNDZYVFpIOWhENVZkWTNDd2NiMmlaQHhWPUIyayk5eG1leFZqbGJeZEh9ZVA6RDN6czdaVW5OZGk3XWFsakhlSy8salZORDZLJ3hZU3JcR0M2On9CY3xuSng2VlpqT2F8QDVTZFk1M2N/QjlZSkczOTpSMmspOFB8b2hWZFk4aHBVaFZlQlhpQ2NOalh1OHtlcHM5V1ZaeUZxbmdRRkY1RH9CMmJmWEhqb0hAVzN0ZWIxOnZRPkFlQWQ7ZFpeSDpjNDIyZFhjQ3djbmJmZTB4UX1CNmE+SXpiNXA2bGJSXGp4dkNpdkQ2emM9ZGRaXmRkd1dVaWpIZkVvJ1RkRlQ4Syd3Q2tjfEdDNjp/QmRsb0RYN1pVcl9icnAyM2heRTZtT0I5X0JXMDk6XmJvKHhfbG9jNFZqWGh/JWdWY0h4aUNzR1RlNGh8b0B3WVZhOnpGcWdVZUpGN0k/SFRUWGhHam9HUmskZGRtYTdSUTpRZkY0N1JlYlg5YzQ6cFJjc0Z3c2tiYlpQd1Y9R1JjNkl4bWV4QmB5Ml5qaH1hWnZUM3pzPmRjVl5mZHddZWtmWGhPTy1kZUpEN0sneFFaaGxFTmY3UWVkbG5KaDdSXGpfYHcwN1lVYlU1aD9KfUxDdzE5OlxiZTpIUHE/aEZmVkhqdnVnRFxGWGtDc0haWXk4e2Vwd1NjUlp6RnFgMWZJNjhEf0dSZlJYR2p/TmZlPkRlZ0E3Slh1MWZBdDIyZlZYOGhEPmJmVTNEd2NoQFJjcHdWPUp2YzZZd21lfWJifGJcamh4RVl2VDN6YzM6Vmh+ZGR3XmFsaHhoT08iOlRGRDhFd3dBXWxsSE5mN0FmXkxvRFg4VGpiX2B3MDdZVGZVM2NvTGFdSUcwNH9JaFM6RGViMTdUYDZBZUF0PWJjZlg3bmQxNmVaQ0R3c2dSYlEwdlF9RUJhOll3bWV3VmxoclxqaHhBWnk0NnpjPWRlWk5maTdSMWN4eGZFfydUY0N0N0snen1CclxFSFY+YWJVPG1KaDM6XWk/b2JwPmlUbkU0Y29IQ2NGVzA0eldSaTJYUHZPZ1JnVkhodnVoUm1CWGlIM0A6XyU4fGVweENjWTp8RnFnQW1GVjVEf05gUmN4SWp/SnhaelRkZ1EwMlp5MWhBdDdWYVk4Om5kPWJmVTNEd2NoSFVaQHVWPUdSay5JeGI1fWJsakJcanh7Y2E1NDN6YzI0ZVxuZmR3UjFldlhoT08nSlZBNDZFd3dZVXJcR0M2On9CY3xtSngxNl1kb29sQDVZVWxlNmN/R1lSQlcxOTpXUmAySF9mX25iZl5IaH8iJ1IsKTc8SydibEFjSWhzUkdVdnFJfT06MihiKW5qRzF5NVEwN0skPkBXdXJ/QzxkamF5NkJZaURJVTxjN1ZhNWBWWy5FQnJ3cXIwMm8nemE5Zn1od2h5XEUzdHljOkR/RDdWWDtmMzVZMi0yLC1GMUVneVtHUk5mdjNUXyJ0aXthQFl9OUoyIWIjZ2FQdXxFOEN9YDlBV3pCcV1CdnlRYjtjQkdvIDBWc0J2e25PLElqYzFZbyFHamFtb2QxeX1kUUFCUnVpeXRWbyp0bmY7J0sgdV1LTUlYSFMzMl1kdEhJeXFZOnczaWsgWFdpQzByWDN/b0RacVpYVzVLbyZDWEl+S2xJUlJHZnppQ3NfRTFxdzNUNVlWdnZDVm9oSVN6dXdkUkNvTE5AMH1KZGJEfU1lf0F1WmJZQFhkakl+SmheY0slUmF4eE5tYVd0NmNUNltIYmU0c1Q4QWRIMFBZUmtkS2tIMFZhNkV0Xy8oUFVhWHc2N3c5OmdyZDlcRENfR21BVlpyZ0dER3tjczRjXm9gOTNwPUZEa0Z3dlBwOk1oPWdOamY3MU9jYlJrIlVidUBXfGgxO2NXWlEyOnFgPGdiU3dhWnIyUXV/JFF7I0RHMHpncDpeaHp+YVFpVE8nVXh8aWgzNGZhWlczY01EZmpgNDVJb2NUUTdYSUBcSXRUeWROZnJjYkk3XUJFeVpxeTM1V3NTUVtoUmlCYmBWRDJBNFRyayF1QFFEaXc2bk5kSHdyOGdKSEc3VHxCcFR0dDh7Rk1kUntIN2JcZkNFPmI6XkBVbUthXkE5ZDRpeDpraDNcZVBxX0UzXENpXyxiVH9tQndrYmxCampGY3FZYX5ieFQzYVVZeEZiTmpcZ0thV2djZ1hYP2psayFWZ3pKVXpFclVkTWkxSnVRQ3NCelFcaXBYX0h5UkpnWWA0cTRhWWpCR0pHYUM7aH9NQVN2NXM/Y3c2SHNPR0hnRG8lVTdIZWFDdGhBS2p/aDM9N2ItMiwtRjJRaGZlRjhoZTYxUlg4WTp5OVoyK2IpSDVZY1siV1VbRkVRVX9pbkU5SmlIMVlmanxgOVNOS21Ef2lgWHR4WklxOmlWRkZYWWAyO0l1Sm5EMipyLCk4Nk9CQWJVYk1odjNHXmJ0cDgwNXp0ZFdLbT1KMiIrVFR0S2Nza0pCeUIxSWFNRWF2V19ram5ma2ZVU3VOSWVpMl5lUHg1cWV6SFpVWlpmYXZZaURkUFZcIiRyK2RTZFpDeUtBQnFJZ1RyLUIsJFR6a2Nza0pCeUIxSWFNRWF2V19ram5ma2ZVVH1OSWFkdldYXGg1cWV1OEpValpkUW5JaURkUFZcIiRyK2RTanpDdTtCQnFIUWN4fUJxemZdN2ItMiwkVHRMY3NrSkJ1OFJDcU1BYXh2UndqbT08IiRyLGRTZFpDdTtCQnFIUWN4fUJxemZdN2ItPC1VMiFtRmhSOH5tTTdiLTIqM2FPZmA0Zk8sIiUyK01FbkV4fmdUOWItMio3e209PXIg==",
                "st": 1667958230,
                "sr": 595521988,
                "cr": 398863270,
            },
            "version": "beta",
        },
        "old_token": None,
        "error": None,
        "performance": {"interrogation": 340},
    }

    access_token: Optional[str] = None

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
        if headers is None:
            headers = {}

        if params is None:
            params = {}

        headers.update(self.DEFAULT_HEADERS)
        counter_tries = 0
        s = requests.Session()

        cookies = {}

        while True:
            try:
                if authorized:
                    if self.access_token is None:
                        raise Exception("Need token to make authorized requests")
                    cookies[self.AUTH_COOKIE_KEY] = self.access_token

                s.cookies.update(cookies)
                counter_tries += 1
                if not request_data is None:
                    response: Response = s.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, data=json.dumps(request_data), timeout=timeout)
                else:
                    response: Response = s.request(method, f"{self.BASE_URL}{end_point}", params=params, headers=headers, timeout=timeout)

                if not response.ok:
                    print(f"Connection error: {response.status_code} try: {counter_tries} page: {end_point}", end="\r")
                    if response.status_code == 401 or response.status_code == 403:
                        self.login()
                        continue
                    if counter_tries > 20:
                        print("Connection error: ", response.status_code)
                        return {}
                    continue

            except Exception:
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

    def login(self):
        # cur_dir = os.path.dirname(os.path.realpath(__file__))
        # with open(os.path.join(cur_dir, "auth_data.json"), "r") as f:
        response: Response = requests.request(
            "POST", "https://pls-sprmrkt-mw.prd.vdc1.plus.nl/Due-away-are-Fight-Banq-Though-theere-Prayers-On?d=pls-sprmrkt-mw.prd.vdc1.plus.nl", data=json.dumps(self.AUTH_DICT_DATA)
        )
        if not response.ok:
            raise Exception("Login failed")

        self.access_token = response.json().get("token")
        return

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

        self.login()

    class Categories:
        def __init__(self, client: Client) -> None:
            self.__client = client
            self.data: Dict[Union[int, str], Client.Category] = {}

        def list(self):
            response = self.__client.request("GET", "categorytree")

            if not isinstance(response, dict):
                raise ValueError("Reponse is not in right format")

            data: List[Dict[str, Any]] = response.get("categories", [])

            for elem in data:
                category = self.__client.Category(self.__client, data=elem)
                self.data[category.id] = category

                sub_categories = elem.get("children", [])

                def get_sub_categories(sub_categories: List[Dict[str, Any]]) -> None:
                    for sub_category in sub_categories:
                        sub_category_elem = self.__client.Category(self.__client, data=sub_category)
                        self.data[sub_category_elem.id] = sub_category_elem
                        get_sub_categories(sub_category.get("children", []))

                get_sub_categories(sub_categories)

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
        def list(self) -> Dict[int, Client.Product]:
            ...

        @typing.overload
        def list(self, category: Client.Category) -> Dict[int, Client.Product]:
            ...

        def list(self, category: Optional[Client.Category] = None):
            category_id = 333333

            self.data[category_id] = {}

            page = 1
            total_pages = 1

            while True:
                response = self.__client.request("GET", f"navigation", params={"tn_cid": category_id, "tn_ps": 1000, "tn_p": page})

                if not isinstance(response, dict):
                    raise ValueError("Expected response to be dict")

                total_pages = response.get("properties", {}).get("nrofpages")

                print(f"{page}/{total_pages}", end="\r")

                products = response.get("items", [])

                for product in products:
                    temp_ = self.__client.Product(self.__client, data=product)
                    if not temp_ is None:
                        if not temp_.id in self.data[category_id].keys():
                            self.data[category_id][temp_.id] = temp_

                if page == total_pages:
                    break

                page += 1

            return self.data[category_id]

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
                id = data.get("itemno")

                if id is None:
                    raise ValueError("Expected data to have ID")

                if not isinstance(id, int) and id.isdigit():
                    id = int(id)

            super().__init__(id)

            if not data is None:
                self.name = data.get("title")
                self.price_current = data.get("price")
                self.brand = data.get("brand")

        def details(self):
            response = self.__client.request("GET", f"product/{self.id}", debug_key="product_details")

            if not isinstance(response, dict):
                raise ValueError("Expected value to be dict")

            data: Dict[str, Any] = response

            self.unit_size = data.get("baseUnit")
            self.unit_size = data.get("unit") if self.unit_size is None else self.unit_size
            self.brand = data.get("merk")
            self.description = data.get("wettelijke_naam")
            self.price_current = data.get("salePrice")
            self.price_raw = data.get("listPrice")
            self.quantity = data.get("ratioBasePackingUnit")
            self.category_id = data.get("mainCategoryId")
            self.category_id = int(self.category_id) if not self.category_id is None and not isinstance(self.category_id, int) and self.category_id.isdigit() else None
            self.category = data.get("mainCategoryName")

            if not self.price_current is None and not self.price_raw is None:
                self.bonus = True if self.price_current < self.price_raw else False

            return self

        def price(self):  # type: ignore
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
                id = data.get("categoryid")

                slug_name = data.get("categorypath")
                name = data.get("title")
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
