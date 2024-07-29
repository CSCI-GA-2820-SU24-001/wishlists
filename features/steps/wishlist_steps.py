import os
import requests
from behave import given

@given('the server is started')
def step_impl(context):
    context.base_url = os.getenv('BASE_URL', 'http://localhost:8080')
    context.resp = requests.get(context.base_url + '/')
    assert context.resp.status_code == 200

@given('the following wishlists')
def step_impl(context):
    for row in context.table:
        wishlist = {
            "name": row["name"],
            "customer_id": row["customer_id"]
        }
        response = requests.post(f"{context.base_url}/wishlists", json=wishlist)
        assert response.status_code == 201

@given('the following wishlist items')
def step_impl(context):
    for row in context.table:
        wishlist_item = {
            "wishlist_id": row["wishlist_id"],
            "product_id": row["product_id"],
            "price": float(row["price"]),
            "description": row["description"]
        }
        response = requests.post(f"{context.base_url}/wishlists/{row['wishlist_id']}/items", json=wishlist_item)
        assert response.status_code == 201

