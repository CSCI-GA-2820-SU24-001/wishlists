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

from unittest.mock import patch
from service.models import Wishlist, WishlistItem, DataValidationError
from tests.factories import WishlistFactory, WishlistItemFactory
from .test_base import TestBase


######################################################################
#    W I S H L I S T   I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlistItem(TestBase):
    """WishlistItem Model Test Cases"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_wishlist_item(self):
        """It should Create an wishlist with an item and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        item = WishlistItemFactory(wishlist=wishlist)
        wishlist.items.append(item)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(new_wishlist.items[0].id, item.id)
        self.assertEqual(new_wishlist.items[0].wishlist_id, item.wishlist_id)
        self.assertEqual(new_wishlist.items[0].product_id, item.product_id)
        self.assertEqual(new_wishlist.items[0].description, item.description)
        self.assertEqual(new_wishlist.items[0].product_id, item.product_id)
        self.assertAlmostEqual(float(new_wishlist.items[0].price), float(item.price))

        item2 = WishlistItemFactory(wishlist=wishlist)
        wishlist.items.append(item2)
        wishlist.update()

        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(new_wishlist.items), 2)
        self.assertEqual(new_wishlist.items[1].id, item2.id)
        self.assertEqual(new_wishlist.items[1].wishlist_id, item2.wishlist_id)
        self.assertEqual(new_wishlist.items[1].product_id, item2.product_id)
        self.assertEqual(new_wishlist.items[1].description, item2.description)
        self.assertEqual(new_wishlist.items[1].product_id, item2.product_id)
        self.assertAlmostEqual(float(new_wishlist.items[1].price), float(item2.price))

    @patch("service.models.db.session.commit")
    def test_add_wishlist_item_failed(self, exception_mock):
        """It should not add an item to wishlist on database error"""
        exception_mock.side_effect = Exception()
        item = WishlistItemFactory()
        self.assertRaises(DataValidationError, item.create)

    def test_delete_wishlist_item(self):
        """It should Delete an wishlist item"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        wishlist = WishlistFactory()
        item = WishlistItemFactory(wishlist=wishlist)
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Fetch it back
        wishlist = Wishlist.find(wishlist.id)
        item = wishlist.items[0]
        item.delete()
        wishlist.update()

        # Fetch it back again
        wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(wishlist.items), 0)

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

    def test_deserialize_item_key_error(self):
        """It should not Deserialize a wishlist item with a KeyError"""
        item = WishlistItem()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize a wishlist item with a TypeError"""
        item = WishlistItem()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_deserialize_item_bad_price_type(self):
        """It should not Deserialize a wishlist item with a TypeError because bad price type"""
        item = WishlistItem()

        data = {}
        data['wishlist_id'] = "0"
        data["product_id"] = "0"
        data["description"] = "desc"
        data["price"] = "123456"  # should be int / float, but set to string here

        self.assertRaises(DataValidationError, item.deserialize, data)
