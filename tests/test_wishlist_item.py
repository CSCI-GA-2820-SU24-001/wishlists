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

"""
Test cases for WishlistItem Model
"""

import logging
import os
from unittest import TestCase
from wsgi import app
from service.models import Wishlist, WishlistItem, db
from tests.factories import WishlistFactory, WishlistItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#    W I S H L I S T   I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlistItem(TestCase):
    """WishlistItem Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(WishlistItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_serialize_a_wishlist_item(self):
        """It should serialize a WishlistItem"""
        wishlist_item = WishlistItemFactory()
        serial_wishlist_item = wishlist_item.serialize()
        self.assertEqual(serial_wishlist_item["id"], wishlist_item.id)
        self.assertEqual(serial_wishlist_item["wishlist_id"], wishlist_item.wishlist_id)
        self.assertEqual(serial_wishlist_item["product_id"], wishlist_item.product_id)
        self.assertEqual(serial_wishlist_item["description"], wishlist_item.description)
        self.assertAlmostEqual(serial_wishlist_item["price"], float(wishlist_item.price))

    def test_deserialize_a_wishlist_item(self):
        """It should deserialize a WishlistItem"""
        wishlist_item = WishlistItemFactory()
        wishlist_item.create()
        new_wishlist_item = WishlistItem()
        new_wishlist_item.deserialize(wishlist_item.serialize())
        self.assertEqual(new_wishlist_item.wishlist_id, wishlist_item.wishlist_id)
        self.assertEqual(new_wishlist_item.product_id, wishlist_item.product_id)
        self.assertEqual(new_wishlist_item.description, wishlist_item.description)
        self.assertAlmostEqual(new_wishlist_item.price, float(wishlist_item.price))




    def test_get_wishlist_item(self):
        """It should Get an existing Wishlist Item"""
        # Create a Wishlist
        wishlist = WishlistFactory()
        wishlist.create()
        wishlist_id = wishlist.id

        # Add an item to the wishlist
        item = WishlistItemFactory(wishlist_id=wishlist_id)
        item.create()
        item_id = item.id

        # Get the item
        resp = self.client.get(f"/wishlists/{wishlist_id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["wishlist_id"], wishlist_id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["description"], item.description)
        self.assertAlmostEqual(data["price"], float(item.price))

    def test_get_wishlist_item_not_found(self):
        """It should not Get a Wishlist Item that does not exist"""
        # Create a Wishlist
        wishlist = WishlistFactory()
        wishlist.create()
        wishlist_id = wishlist.id

        # Try to get a non-existent item
        resp = self.client.get(f"/wishlists/{wishlist_id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])
