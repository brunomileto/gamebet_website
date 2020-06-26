import pprint
from flask import url_for
import mercadopago
import json
import os, sys
from gamebet_website.app.models.models import Sale



ACCESS_TOKEN = "TEST-6845351963416569-061712-44cd2b44c62a0c11170bd5a901d6f32f-585866733"

mp = mercadopago.MP(ACCESS_TOKEN)


def payment(req, **kwargs):
    product = kwargs['product']
    current_user_id = kwargs['current_user_id']
    external_reference = [current_user_id]
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
        "external_reference": external_reference
    }

    preference_result = mp.create_preference(preference)

    preference_id = preference_result['response']['id']
    external_reference.append(preference_id)

    final_preference = {
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
        "external_reference": external_reference
    }


    preference_result_complete = mp.update_preference(preference_id, final_preference)


    product_url = preference_result_complete['response']['init_point']
    return [product_url, preference_result_complete]


def get_payment_info(req, **kwargs):
    payment_info = mp.get_payment(req["data.id"])
    pprint.pprint(payment_info)
    print(type(payment_info))

    external_reference = payment_info['response']['external_reference']
    external_reference = external_reference.replace('[','')
    external_reference = external_reference.replace(']','')
    external_reference = external_reference.replace('"','')
    external_reference = external_reference.split(', ')

    print(type(external_reference))

    for index in range(len(external_reference)):
        print(external_reference[index])


    user_id = external_reference[0]
    preference_id = external_reference[1]

    return [payment_info, preference_id, user_id]













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
