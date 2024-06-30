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
Test cases for Wishlist Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Wishlist, WishlistItem, DataValidationError, db
from .factories import WishlistFactory, WishlistItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlist(TestCase):
    """Wishlist Model Test Cases"""

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
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_wishlist(self):
        """It should Create an Wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name,
            customer_id=fake_wishlist.customer_id,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.items, [])
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.customer_id, fake_wishlist.customer_id)

    def test_delete_a_wishlist(self):
        """It should Delete a Wishlist"""
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist(
            name=fake_wishlist.name,
            customer_id=fake_wishlist.customer_id,
        )
        wishlist.create()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist
        wishlist.delete()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_delete_wishlist_not_found(self):
        """It should not delete a Wishlist that does not exist"""
        wishlist = Wishlist()
        self.assertIsNone(wishlist.id)
        result = wishlist.delete()
        self.assertIsNone(result)

    def test_update_wishlist(self):
        """It should Update a wishlist"""
        wishlist = WishlistFactory(name="Holiday Wishlist")
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        self.assertEqual(wishlist.name, "Holiday Wishlist")

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        wishlist.name = "Birthday Wishlist"
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(wishlist.name, "Birthday Wishlist")

    @patch("service.models.db.session.commit")
    def test_update_wishlist_failed(self, exception_mock):
        """It should not update a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.update)

    def test_find_by_name(self):
        """It should Find a Wishlist by name"""
        wishlist = WishlistFactory(name="Holiday Wishlist")
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.name, wishlist.name)

    def test_serialize_a_wishlist(self):
        """It should Serialize a wishlist"""
        wishlist = WishlistFactory()
        wishlist_item = WishlistItemFactory()
        wishlist.items.append(wishlist_item)
        serial_wishlist = wishlist.serialize()
        self.assertEqual(serial_wishlist["id"], wishlist.id)
        self.assertEqual(serial_wishlist["customer_id"], wishlist.customer_id)
        self.assertEqual(serial_wishlist["name"], wishlist.name)
        self.assertEqual(len(serial_wishlist["items"]), 1)
        items = serial_wishlist["items"]
        self.assertEqual(items[0]["id"], wishlist_item.id)
        self.assertEqual(items[0]["product_id"], wishlist_item.product_id)
        self.assertEqual(items[0]["description"], wishlist_item.description)
        self.assertEqual(items[0]["price"], float(wishlist_item.price))

    def test_deserialize_a_wishlist(self):
        """It should Deserialize a wishlist"""
        wishlist = WishlistFactory()
        wishlist.items.append(WishlistItemFactory())
        wishlist.create()
        serial_wishlist = wishlist.serialize()
        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.customer_id, wishlist.customer_id)
        self.assertEqual(new_wishlist.name, wishlist.name)
        self.assertEqual(len(new_wishlist.items), len(wishlist.items))

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a wishlist with a KeyError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a wishlist with a TypeError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize a wishlist item with a KeyError"""
        item = WishlistItem()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize a wishlist item with a TypeError"""
        item = WishlistItem()
        self.assertRaises(DataValidationError, item.deserialize, [])
