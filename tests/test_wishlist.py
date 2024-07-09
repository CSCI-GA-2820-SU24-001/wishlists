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

from unittest.mock import patch
from service.models import Wishlist, DataValidationError
from .factories import WishlistFactory, WishlistItemFactory
from .test_base import TestBase


######################################################################
#        W I S H L I S T   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlist(TestBase):
    """Wishlist Model Test Cases"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should Create an Wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        wishlist = Wishlist()
        wishlist.name = fake_wishlist.name
        wishlist.customer_id = fake_wishlist.customer_id
        wishlist.items = []

        print(repr(wishlist))

        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.items, [])
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.customer_id, fake_wishlist.customer_id)

    def test_add_a_wishlist(self):
        """It should Create an wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    @patch("service.models.db.session.commit")
    def test_add_wishlist_failed(self, exception_mock):
        """It should not create an Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.create)

    def test_read_a_wishlist(self):
        """It should Read a Wishlist"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            name=fake_wishlist.name,
            customer_id=fake_wishlist.customer_id,
            items=[]
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
        wishlist = WishlistFactory()
        wishlist.id = "non-existent-id"  # Set an ID that does not exist in the database
        self.assertRaises(DataValidationError, wishlist.delete)

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

    def test_list_all_wishlists(self):
        """It should List all Wishlists in the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        for wishlist in WishlistFactory.create_batch(5):
            wishlist.create()
        # Assert that there are not 5 wishlists in the database
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 5)

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
