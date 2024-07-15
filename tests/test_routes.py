"""
WishlistModel API Service Test Suite
"""
import uuid
import logging
from service.common import status
from .factories import WishlistFactory, WishlistItemFactory
from .test_base import TestBase

BASE_URL = "/wishlists"


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
        """It should Accept a POST request and Create a new Wishlist, but not for duplicate ones"""
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
            new_wishlist["customer_id"],
            wishlist.customer_id,
            "customer id does not match",
        )
        self.assertEqual(new_wishlist["items"], wishlist.items, "Items does not match")

        # resp = self.client.post(
        #     BASE_URL, json=wishlist.serialize(), content_type="application/json"
        # )
        # self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_delete_wishlist(self):
        """It should Delete a wishlist"""
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
        wishlist_id = wishlist.id

        # Try to get a item from non-existent wishlist
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
            WishlistItemFactory(price=20)
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(f"/wishlists/{wishlist.id}/items/sort?order=asc")
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
            WishlistItemFactory(price=20)
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(f"/wishlists/{wishlist.id}/items/sort?order=desc")
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
            WishlistItemFactory(price=30)
        ]
        wishlist.items = items
        wishlist.create()

        response = self.client.get(f"/wishlists/{wishlist.id}/items/sort")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["price"], 10)
        self.assertEqual(data[1]["price"], 20)
        self.assertEqual(data[2]["price"], 30)

    def test_sort_items_in_nonexistent_wishlist(self):
        """Test sorting items in a non-existent wishlist"""
        response = self.client.get("/wishlists/nonexistent-id/items/sort")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("could not be found", data["message"])

    def test_get_wishlists_by_customer_id(self):
        """Test retrieving wishlists by customer ID"""
        customer_id = str(uuid.uuid4())
        wishlist1 = WishlistFactory(customer_id=customer_id)
        wishlist2 = WishlistFactory(customer_id=customer_id)
        wishlist1.create()
        wishlist2.create()

        response = self.client.get(f"/wishlists/customers/{customer_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_get_wishlists_by_nonexistent_customer_id(self):
        """Test retrieving wishlists by non-existent customer ID"""
        response = self.client.get("/wishlists/customers/nonexistent-customer-id")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("No wishlists found for customer id", data["message"])

    def test_query_wishlist_item_by_price(self):
        """It should Query wishlist item by price"""

        wishlist = self._create_wishlists(1)[0]
        item_list = WishlistItemFactory.create_batch(5)
        for i in range(5):
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
                item["price"] < test_price,
                f"Item {item['id']} has a price of {item['price']} which is not less than {test_price}",
            )
