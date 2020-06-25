import pprint
from flask import url_for
import mercadopago
import json
import os, sys


ACCESS_TOKEN = "TEST-6845351963416569-061712-44cd2b44c62a0c11170bd5a901d6f32f-585866733"

mp = mercadopago.MP(ACCESS_TOKEN)


def payment(req, **kwargs):
    product = kwargs['product']
    preference = {
        "items": [
            {
                "id": product.id,
                "title": product.product_name,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": product.product_value
            }
        ],
        "back_urls":
            {
                "success": f"http://127.0.0.1:5000/resultado_compra.html",
                "failure": "http://127.0.0.1:5000/resultado_compra.html",
                "pending": "http://127.0.0.1:5000/resultado_compra.html"
            },
        "auto_return": 'approved',
        "external_reference": 'kak'
    }
    preference_result = mp.create_preference(preference)
    pprint.pprint(preference_result)
    print('------------')
    pprint.pprint(preference)
    print('-------------')
    product_url = preference_result['response']['init_point']
    pprint.pprint(product_url)
    return [product_url, preference_result]















# { VENDEDOR
#     "id": 585907376,
#     "nickname": "TESTNSLXOOWL",
#     "password": "qatest8068",
#     "site_status": "active",
#     "email": "test_user_91336806@testuser.com"
# }

# { COMPRADOR
#     "id": 585909164,
#     "nickname": "TETE113266",
#     "password": "qatest7747",
#     "site_status": "active",
#     "email": "test_user_60308303@testuser.com"
# }
