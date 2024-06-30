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

    def test_update_wishlist_item(self):
        """It should Update a wishlist item"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        wishlist = WishlistFactory()
        wishlist_item = WishlistItemFactory(wishlist=wishlist)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        old_item = wishlist.items[0]
        print("%r", old_item)
        self.assertEqual(old_item.description, wishlist_item.description)
        # Change the description
        old_item.description = "Updated description"
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        item = wishlist.items[0]
        self.assertEqual(item.description, "Updated description")
