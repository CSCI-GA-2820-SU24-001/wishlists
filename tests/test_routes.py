"""
WishlistModel API Service Test Suite
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Wishlist
from .factories import WishlistFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/wishlists"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class WishlistService(TestCase):
    """ REST API Server Tests """

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
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
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
            new_wishlist["customer_id"], wishlist.customer_id, "customer id does not match"
        )
        self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")

        # TODO: Uncomment this code when get_wishlists is implemented
        # # Check that the location header was correct by getting it
        # resp = self.client.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_wishlist = resp.get_json()
        # self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        # self.assertEqual(
        #     new_wishlist["customer_id"], wishlist.customer_id, "customer id does not match"
        # )
        # self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")
