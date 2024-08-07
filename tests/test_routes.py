"""
Test cases for WishlistModel API Service
"""

import logging
from datetime import date
import uuid
from service.common import status
from .factories import WishlistFactory, WishlistItemFactory
from .test_base import TestBase

BASE_URL = "/api/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class WishlistService(TestBase):
    """REST API Server Tests"""

    ######################################################################
    #  HELPER FUNCTIONS HERE
    ######################################################################

    def _create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            wishlist.customer_id = (
                "Customer" + str(uuid.uuid4())[:36]
            )  # Ensure customer_id is a String and within length constraints
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
        wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
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
            new_wishlist["customer_id"],
            wishlist.customer_id,
            "customer id does not match",
        )
        self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")

        tmp = wishlist.customer_id
        wishlist.customer_id = ""
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        wishlist.customer_id = tmp
        wishlist.name = ""
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_wishlist(self):
        """It should Delete a wishlist"""
        # create a wishlist to be deleted
        wishlist = WishlistFactory()
        wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
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
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

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
        test_wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
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

    def test_update_wishlist_not_exist(self):
        """It should not Update a Wishlist that does not exist"""
        # create a Wishlist to update
        test_wishlist = WishlistFactory()
        test_wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
        resp = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the wishlist
        new_wishlist = resp.get_json()
        new_wishlist["name"] = "Updated Wishlist Name"
        new_wishlist_id = "0"
        resp = self.client.put(f"{BASE_URL}/{new_wishlist_id}", json=new_wishlist)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_get_wishlist(self):
        """It should Get an existing Wishlist"""
        # Create a Wishlist to read
        test_wishlist = WishlistFactory()
        test_wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
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

    def test_query_wishlists_by_name(self):
        """It should query and return a list of wishlists of the specified name"""
        # create 3 wishlists
        wishlists = self._create_wishlists(3)
        resp = self.client.get(f"{BASE_URL}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 3)

        # change the names of 2 wishlists as "myWishlist"
        wishlists[0].name = "myWishlist"
        wishlists[1].name = "myWishlist"
        wishlists[2].name = "notMyWishlist"

        # update the wishlists
        resp = self.client.put(
            f"{BASE_URL}/{wishlists[0].id}",
            json=wishlists[0].serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.put(
            f"{BASE_URL}/{wishlists[1].id}",
            json=wishlists[1].serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.put(
            f"{BASE_URL}/{wishlists[2].id}",
            json=wishlists[2].serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.get(f"{BASE_URL}?name=myWishlist")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(wishlists[0].name, data[0]["name"])
        self.assertEqual(wishlists[0].name, data[1]["name"])

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")

    ######################################################################
    #  WISHLIST ITEMS TEST CASES HERE
    ######################################################################

    def test_update_wishlist_item(self):
        """It should Update a wishlist item in a wishlist"""
        # create a known wishlist and wishlist item
        wishlist = self._create_wishlists(1)[0]
        wishlist_item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=wishlist_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        data["description"] = "Updated description"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["description"], "Updated description")

    def test_update_wishlist_item_not_exist(self):
        """It should not Update a wishlist item that does not exist"""
        # create a known wishlist and wishlist item
        wishlist = self._create_wishlists(1)[0]
        wishlist_item = WishlistItemFactory()

        data = wishlist_item.serialize()
        item_id = data["id"]

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_wishlist_item(self):
        """It should Get an existing Wishlist Item"""
        # Create a Wishlist
        wishlist = WishlistFactory()
        wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_wishlist = resp.get_json()
        wishlist_id = new_wishlist["id"]

        # Add an item to the wishlist
        item = WishlistItemFactory(wishlist_id=wishlist_id)
        resp = self.client.post(
            f"{BASE_URL}/{wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
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
        wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
        wishlist_id = wishlist.id

        # Try to get an item from non-existent wishlist
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

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
        item.wishlist_id = wishlist.id  # Ensure wishlist_id is properly set
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

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(
            new_item["product_id"], item.product_id, "Item's product_id does not match"
        )

        tmp = item.wishlist_id
        item.wishlist_id = ""
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        item.wishlist_id = tmp
        item.product_id = ""
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_wishlist_not_exist(self):
        """It cannot find the wishlist that does not exist, and return 404"""
        wishlist_id = "wishlist_not_exist"
        item = WishlistItemFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_list(self):
        """It should Get a list of wishlist items"""
        # add two items to wishlist
        wishlist = self._create_wishlists(1)[0]
        item_list = WishlistItemFactory.create_batch(2)

        # get the list back and make sure it is empty, since we haven't add item into wishlist yet
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 0)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items", json=item_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_item_list_not_exist(self):
        """It cannot find the wishlist that does not exist, and return 404"""
        wishlist_id = "wishlist_not_exist"
        resp = self.client.get(f"{BASE_URL}/{wishlist_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item(self):
        """It should Delete an Item if the wishlist and the items exist"""
        wishlist = self._create_wishlists(1)[0]
        item = WishlistItemFactory()
        item.wishlist_id = wishlist.id  # Ensure wishlist_id is properly set
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # try delete again and should return 204
        resp = self.client.delete(
            f"{BASE_URL}/{wishlist.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_move_item_to_another_wishlist(self):
        """It should Move an item from one wishlist to another"""
        # Create two wishlists
        source_wishlist = WishlistFactory()
        target_wishlist = WishlistFactory(customer_id=source_wishlist.customer_id)

        source_wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
        target_wishlist.customer_id = (
            source_wishlist.customer_id
        )  # Ensure same customer_id

        # Add source wishlist to the database
        resp = self.client.post(
            BASE_URL, json=source_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        source_wishlist_id = resp.get_json()["id"]

        # Add target wishlist to the database
        resp = self.client.post(
            BASE_URL, json=target_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        target_wishlist_id = resp.get_json()["id"]

        # Add an item to the source wishlist
        item = WishlistItemFactory()
        item.wishlist_id = source_wishlist_id  # Ensure wishlist_id is properly set
        resp = self.client.post(
            f"{BASE_URL}/{source_wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.get_json()["id"]

        # Move the item to the target wishlist
        resp = self.client.put(
            f"{BASE_URL}/{source_wishlist_id}/items/{item_id}/move-to/{target_wishlist_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify the item is now in the target wishlist
        resp = self.client.get(
            f"{BASE_URL}/{target_wishlist_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["wishlist_id"], target_wishlist_id)

        # Verify the item is no longer in the source wishlist
        resp = self.client.get(
            f"{BASE_URL}/{source_wishlist_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_move_item_to_another_wishlist_bad_path(self):
        """It should not Move an item from one wishlist to another"""
        # Create two wishlists
        source_wishlist = WishlistFactory()
        target_wishlist = WishlistFactory(customer_id=source_wishlist.customer_id)
        other_wishlist = WishlistFactory(customer_id="other_customer")

        source_wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
        target_wishlist.customer_id = (
            source_wishlist.customer_id
        )  # Ensure same customer_id
        other_wishlist.customer_id = "other_customer"  # Different customer_id

        # Add source wishlist to the database
        resp = self.client.post(
            BASE_URL, json=source_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        source_wishlist_id = resp.get_json()["id"]

        # Add target wishlist to the database
        resp = self.client.post(
            BASE_URL, json=target_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        target_wishlist_id = resp.get_json()["id"]

        # Add other wishlist to the database
        resp = self.client.post(
            BASE_URL, json=other_wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        other_wishlist_id = resp.get_json()["id"]

        # Add an item to the source wishlist
        item = WishlistItemFactory()
        item.wishlist_id = source_wishlist_id  # Ensure wishlist_id is properly set
        resp = self.client.post(
            f"{BASE_URL}/{source_wishlist_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.get_json()["id"]

        # Deny when the source wishlist does not exist
        resp = self.client.put(
            f"{BASE_URL}/null/items/{item_id}/move-to/{target_wishlist_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Deny when the target wishlist does not exist
        resp = self.client.put(
            f"{BASE_URL}/{source_wishlist_id}/items/{item_id}/move-to/null",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Deny when the item does not exist
        resp = self.client.put(
            f"{BASE_URL}/{source_wishlist_id}/items/null/move-to/{target_wishlist_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Deny when the customer id does not match
        resp = self.client.put(
            f"{BASE_URL}/{source_wishlist_id}/items/{item_id}/move-to/{other_wishlist_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_content_type(self):
        """It should not Accept any request that have an invalid content type"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="bullshit"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_bad_request(self):
        """It should not Accept any bad requests"""
        data = {}
        data["attr"] = "nonsense"  # malformed data that the server cannot parse
        resp = self.client.post(BASE_URL, json=data, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_method_not_supported(self):
        """It should not Accept any requests with unsupported methods"""
        resp = self.client.post("/", json={}, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_sort_wishlist_items_by_price_ascending(self):
        """Test sorting wishlist items by price in ascending order"""
        wishlist = WishlistFactory()
        items = [
            WishlistItemFactory(price=10),
            WishlistItemFactory(price=30),
            WishlistItemFactory(price=20),
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(
            f"/wishlists/{wishlist.id}/items?sort_by=price&order=asc"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["price"], 10)
        self.assertEqual(data[1]["price"], 20)
        self.assertEqual(data[2]["price"], 30)

    def test_sort_wishlist_items_by_price_descending(self):
        """Test sorting wishlist items by price in descending order"""
        wishlist = WishlistFactory()
        items = [
            WishlistItemFactory(price=10),
            WishlistItemFactory(price=30),
            WishlistItemFactory(price=20),
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(
            f"/wishlists/{wishlist.id}/items?sort_by=price&order=desc"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["price"], 30)
        self.assertEqual(data[1]["price"], 20)
        self.assertEqual(data[2]["price"], 10)

    def test_sort_wishlist_items_by_price_default_order(self):
        """Test sorting wishlist items by price with default (ascending) order"""
        wishlist = WishlistFactory()
        items = [
            WishlistItemFactory(price=20),
            WishlistItemFactory(price=10),
            WishlistItemFactory(price=30),
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(f"/wishlists/{wishlist.id}/items?sort_by=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["price"], 10)
        self.assertEqual(data[1]["price"], 20)
        self.assertEqual(data[2]["price"], 30)

    def test_sort_items_in_nonexistent_wishlist(self):
        """Test sorting items in a non-existent wishlist"""
        response = self.client.get(
            "/wishlists/nonexistent-id/items?sort_by=price|added_date"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("could not be found", data["message"])

    def test_sort_wishlist_items_by_added_date_ascending(self):
        """Test sorting wishlist items by added date in ascending order"""
        wishlist = WishlistFactory()
        items = [
            WishlistItemFactory(added_date=date(2022, 3, 12)),
            WishlistItemFactory(added_date=date(2022, 3, 13)),
            WishlistItemFactory(added_date=date(2022, 3, 14)),
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(
            f"/wishlists/{wishlist.id}/items?sort_by=added_date&order=asc"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data[0]["added_date"],
            date(2022, 3, 12).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        self.assertEqual(
            data[1]["added_date"],
            date(2022, 3, 13).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        self.assertEqual(
            data[2]["added_date"],
            date(2022, 3, 14).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )

    def test_sort_wishlist_items_by_added_date_descending(self):
        """Test sorting wishlist items by added date in descending order"""
        wishlist = WishlistFactory()
        items = [
            WishlistItemFactory(added_date=date(2022, 3, 12)),
            WishlistItemFactory(added_date=date(2022, 3, 14)),
            WishlistItemFactory(added_date=date(2022, 3, 13)),
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(
            f"/wishlists/{wishlist.id}/items?sort_by=added_date&order=desc"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data[0]["added_date"],
            date(2022, 3, 14).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        self.assertEqual(
            data[1]["added_date"],
            date(2022, 3, 13).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        self.assertEqual(
            data[2]["added_date"],
            date(2022, 3, 12).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )

    def test_sort_wishlist_items_by_added_date_default_order(self):
        """Test sorting wishlist items by added date in default (descending) order"""
        wishlist = WishlistFactory()
        items = [
            WishlistItemFactory(added_date=date(2022, 3, 13)),
            WishlistItemFactory(added_date=date(2022, 3, 12)),
            WishlistItemFactory(added_date=date(2022, 3, 14)),
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(f"/wishlists/{wishlist.id}/items?sort_by=added_date")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data[0]["added_date"],
            date(2022, 3, 14).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        self.assertEqual(
            data[1]["added_date"],
            date(2022, 3, 13).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )
        self.assertEqual(
            data[2]["added_date"],
            date(2022, 3, 12).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        )

    def test_query_wishlists_by_customer_id(self):
        """It should Query Wishlists by Customer ID"""
        customer_id = "Customer12345"
        wishlist1 = WishlistFactory(customer_id=customer_id)
        wishlist2 = WishlistFactory(customer_id=customer_id)
        self.client.post(
            BASE_URL, json=wishlist1.serialize(), content_type="application/json"
        )
        self.client.post(
            BASE_URL, json=wishlist2.serialize(), content_type="application/json"
        )

        resp = self.client.get(f"{BASE_URL}?customer_id={customer_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["customer_id"], customer_id)
        self.assertEqual(data[1]["customer_id"], customer_id)

    def test_query_wishlist_item_by_price(self):
        """It should Query wishlist item by price"""

        wishlist = self._create_wishlists(1)[0]
        item_list = WishlistItemFactory.create_batch(5)
        for i in range(5):
            item_list[i].wishlist_id = wishlist.id  # Ensure wishlist_id is properly set
            resp = self.client.post(
                f"{BASE_URL}/{wishlist.id}/items",
                json=item_list[i].serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

        test_price = 50
        filtered_count = len([item for item in item_list if item.price <= test_price])
        response = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items", query_string=f"price={test_price}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), filtered_count)
        # check the data just to be sure
        for item in data:
            self.assertTrue(
                item["price"] <= test_price,
                f"Item {item['id']} has a price of {item['price']} which is not less than {test_price}",
            )

    def test_delete_all_wishlists_by_customer_id(self):
        """It should delete all wishlist for specific customer"""
        customer_id = "fake_customer_id"
        for _ in range(5):
            fake_wishlist = WishlistFactory()
            fake_wishlist.customer_id = (
                customer_id  # Ensure customer_id is properly set
            )
            resp = self.client.post(
                BASE_URL,
                json=fake_wishlist.serialize(),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"{BASE_URL}?customer_id={customer_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
        response = self.client.delete(f"{BASE_URL}/customers/{customer_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        not_exist_customer_id = "fake_customer_id_2"
        response = self.client.delete(f"{BASE_URL}/customers/{not_exist_customer_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_all_items_by_wishlist_id(self):
        """It should delete all items for a specific wishlist"""
        wishlist = WishlistFactory()
        wishlist.customer_id = (
            "Customer" + str(uuid.uuid4())[:36]
        )  # Ensure customer_id is a String and within length constraints
        items = [WishlistItemFactory(), WishlistItemFactory(), WishlistItemFactory()]
        wishlist.items = items
        wishlist.create()

        # Delete all items
        response = self.client.delete(f"{BASE_URL}/{wishlist.id}/items")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Fetch the wishlist and ensure items are deleted
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/items",
            content_type="application/json",
        )
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(len(data), 0)
