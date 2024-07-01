"""
WishlistModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Wishlist, WishlistItem
from .factories import WishlistFactory, WishlistItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class WishlistService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(WishlistItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  HELPER FUNCTIONS HERE
    ######################################################################

    def _create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Wishlist",
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists


    ######################################################################
    #  WISHLIST TEST CASES HERE
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_wishlist(self):
        """It should Accept a POST request and Create a new Wishlist"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(
            new_wishlist["customer_id"],
            wishlist.customer_id,
            "customer id does not match",
        )
        self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(
            new_wishlist["customer_id"], wishlist.customer_id, "customer id does not match"
        )
        self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")
    
    def test_delete_wishlist(self):
        """It should delete a wishlist"""
        # create a wishlist to be deleted
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_wishlist = resp.get_json()
        wishlist_id = new_wishlist["id"]

        # delete the wishlist
        resp = self.client.delete(f"{BASE_URL}/{wishlist_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # check that the wishlist is deleted
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist_not_found(self):
        """It should not delete a wishlist that does not exist"""
        # try to delete a wishlist that doesn't exist
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wishlist_list(self):
        """It should Get a list of Wishlists"""
        self._create_wishlists(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_update_wishlist(self):
        """It should Update an existing Wishlist"""
        # create a Wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the wishlist
        new_wishlist = resp.get_json()
        new_wishlist["name"] = "Updated Wishlist Name"
        new_wishlist_id = new_wishlist["id"]
        resp = self.client.put(f"{BASE_URL}/{new_wishlist_id}", json=new_wishlist)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "Updated Wishlist Name")

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_wishlist(self):
        """It should Get an existing Wishlist""" 
        # Create a Wishlist to read
        test_wishlist = WishlistFactory()
        resp = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Read the wishlist
        new_wishlist = resp.get_json()
        new_wishlist_id = new_wishlist["id"]
        resp = self.client.get(f"{BASE_URL}/{new_wishlist_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_wishlist_not_found(self):
        """It should not Get a Wishlist thats not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])


    ######################################################################
    #  WISHLIST ITEMS TEST CASES HERE
    ######################################################################

    def test_get_wishlist_item(self):
        """It should Get an existing Wishlist Item"""
        # Create a Wishlist
        wishlist = WishlistFactory()
        resp = self.client.post(BASE_URL, json=wishlist.serialize(), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_wishlist = resp.get_json()
        wishlist_id = new_wishlist["id"]

        # Add an item to the wishlist
        item = WishlistItemFactory(wishlist_id=wishlist_id)
        resp = self.client.post(f"{BASE_URL}/{wishlist_id}/items", json=item.serialize(), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_item = resp.get_json()
        item_id = new_item["id"]

        # Get the item
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items/{item_id}")
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
        resp = self.client.post(BASE_URL, json=wishlist.serialize(), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_wishlist = resp.get_json()
        wishlist_id = new_wishlist["id"]

        # Try to get a non-existent item
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_add_item(self):
        """It should Add an item to an wishlist"""
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["description"], item.description)
        self.assertEqual(data["product_id"], item.product_id)

        # TODO: uncomment after get_item_from_wishlist is implemented
        # # Check that the location header was correct by getting it
        # resp = self.client.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_item = resp.get_json()
        # self.assertEqual(new_item["product_id"], item.product_id, "Item's product_id does not match")    

    def test_add_item_wishlist_not_exist(self):
        """It cannot find the wishlist that does not exist, and return 404 """
        wishlist_id = "wishlist_not_exist"
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

