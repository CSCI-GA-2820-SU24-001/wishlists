######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined
# flake8: noqa
"""
Wishlist Steps

Steps file for Wishlists.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 120


@given("the following wishlists")
def step_impl(context):
    """Delete all Wishlists and load new ones"""

    # Get a list all of the wishlists
    rest_endpoint = f"{context.base_url}/api/wishlists"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for wishlist in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{wishlist['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new wishlists
    for row in context.table:
        payload = {"customer_id": row["customer_id"], "name": row["name"]}
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given("the following wishlist items")
def step_impl(context):
    """Delete all Wishlist Items and load new ones"""

    # Get a list all of the wishlists
    rest_endpoint = f"{context.base_url}/api/wishlists"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == HTTP_200_OK
    # Delete all wishlist items in the wishlists one by one
    wishlist_ids = []
    for wishlist in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{wishlist['id']}/items", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)
        wishlist_ids.append(wishlist["id"])

    # Load the database with new wishlist items
    wishlist_index = 0  # Initialize index to assign wishlists
    for row in context.table:
        wishlist_id = wishlist_ids[wishlist_index]  # Get the wishlist ID by index
        payload = {
            "wishlist_id": wishlist_id,
            "product_id": int(row["product_id"]),
            "description": row["description"],
            "price": float(row["price"]),
        }
        context.resp = requests.post(
            f"{rest_endpoint}/{wishlist_id}/items", json=payload, timeout=WAIT_TIMEOUT
        )
        assert context.resp.status_code == HTTP_201_CREATED
        # Move to the next wishlist after assigning an items to the current wishlist
        wishlist_index = wishlist_index + 1
