import os
import requests
from behave import given
import logging

logger = logging.getLogger('behave.steps')

@given('the server is started')
def step_impl(context):
    context.base_url = os.getenv('BASE_URL', 'http://localhost:8080')
    context.resp = requests.get(context.base_url + '/')
    assert context.resp.status_code == 200

@given('the following wishlists')
def step_impl(context):
    context.wishlist_ids = {}
    for row in context.table:
        wishlist = {
            "name": row["name"],
            "customer_id": row["customer_id"]
        }
        response = requests.post(f"{context.base_url}/wishlists", json=wishlist)
        logger.info(f"Creating wishlist: {wishlist}")
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.content}")
        assert response.status_code == 201, f"Error creating wishlist: {response.content}"
        response_data = response.json()
        context.wishlist_ids[row["name"]] = response_data["id"]

@given('the following wishlist items')
def step_impl(context):
    for row in context.table:
        wishlist_id = context.wishlist_ids.get(row["wishlist_id"])
        wishlist_item = {
            "wishlist_id": wishlist_id,
            "product_id": row["product_id"],
            "price": float(row["price"]),
            "description": row["description"]
        }
        response = requests.post(f"{context.base_url}/wishlists/{wishlist_id}/items", json=wishlist_item)
        logger.info(f"Creating wishlist item: {wishlist_item}")
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.content}")
        assert response.status_code == 201, f"Error creating wishlist item: {response.content}"
        