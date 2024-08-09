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
Wishlist Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlists and Wishlist Items
"""

from flask_restx import Resource, fields, reqparse
from service.models import Wishlist, WishlistItem
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# GET INDEX
######################################################################
@api.route("/")
class IndexResource(Resource):
    """Base URL for Wishlist service"""

    def get(self):
        """Returns the index page"""
        return api.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@api.route("/health")
class HealthCheckResource(Resource):
    """Health Status"""

    def get(self):
        """Performs health check"""
        return {"status": "OK"}, status.HTTP_200_OK


# Define the models so that the docs reflect what can be sent
create_wishlist_model = api.model(
    "Wishlist",
    {
        "customer_id": fields.String(
            required=True, description="The ID of the customer"
        ),
        "name": fields.String(required=True, description="The name of the wishlist"),
        "items": fields.List(
            fields.Nested(
                api.model(
                    "WishlistItem",
                    {
                        "product_id": fields.String(
                            required=True, description="The ID of the product"
                        ),
                        "description": fields.String(
                            description="Description of the item"
                        ),
                        "price": fields.Float(
                            required=True, description="Price of the item"
                        ),
                    },
                )
            ),
            description="List of items in the wishlist",
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "created_date": fields.Date(description="The date the wishlist was created"),
        "modified_date": fields.Date(
            description="The date the wishlist was last modified"
        ),
    },
)

# Query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "customer_id",
    type=str,
    location="args",
    required=False,
    help="List Wishlists by customer_id",
)
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="List Wishlists by name"
)

item_model = api.model(
    "WishlistItem",
    {
        "product_id": fields.String(required=True, description="The ID of the product"),
        "description": fields.String(description="Description of the item"),
        "price": fields.Float(required=True, description="Price of the item"),
        "wishlist_id": fields.String(
            required=True, description="The ID of the wishlist"
        ),
    },
)


######################################################################
#  PATH: /wishlists/{id}
######################################################################
@api.route("/wishlists/<wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """
    WishlistResource class

    Allows the manipulation of a single Wishlist
    GET /wishlists/{id} - Returns a Wishlist with the id
    PUT /wishlists/{id} - Update a Wishlist with the id
    DELETE /wishlists/{id} -  Deletes a Wishlist with the id
    """

    @api.doc("get_wishlists")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist

        This endpoint will return a Wishlist based on its id
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc("update_wishlists")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist

        This endpoint will update a Wishlist based on the body that is posted
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        wishlist.deserialize(api.payload)
        wishlist.id = wishlist_id
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc("delete_wishlists")
    @api.response(204, "Wishlist deleted")
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based on its id
        """
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists
######################################################################
@api.route("/wishlists", strict_slashes=False)
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    @api.doc("list_wishlists")
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """Returns all of the Wishlists"""
        args = wishlist_args.parse_args()
        if args["customer_id"]:
            wishlists = Wishlist.find_by_customer_id(args["customer_id"])
        elif args["name"]:
            wishlists = Wishlist.find_by_name(args["name"])
        else:
            wishlists = Wishlist.all()

        return [wishlist.serialize() for wishlist in wishlists], status.HTTP_200_OK

    @api.doc("create_wishlists")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist

        This endpoint will create a Wishlist based on the data in the body that is posted
        """
        wishlist = Wishlist()
        wishlist.deserialize(api.payload)
        wishlist.create()
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )
        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/{wishlist_id}/items
######################################################################
@api.route("/wishlists/<wishlist_id>/items")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistItemCollection(Resource):
    """Handles all interactions with collections of WishlistItems"""

    @api.doc("list_wishlist_items")
    @api.marshal_list_with(item_model)
    def get(self, wishlist_id):
        """Returns all of the items for a Wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        return [item.serialize() for item in wishlist.items], status.HTTP_200_OK

    @api.doc("create_wishlist_item")
    @api.response(400, "The posted Wishlist Item data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, wishlist_id):
        """
        Creates an Item in a Wishlist

        This endpoint will add an item to a wishlist based on the data in the body that is posted
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = WishlistItem()
        item.deserialize(api.payload)
        item.wishlist_id = wishlist_id  # Ensure wishlist_id is set
        wishlist.items.append(item)
        wishlist.update()
        location_url = api.url_for(
            WishlistItemResource,
            wishlist_id=wishlist.id,
            item_id=item.id,
            _external=True,
        )
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/{wishlist_id}/items/{item_id}
######################################################################
@api.route("/wishlists/<wishlist_id>/items/<item_id>")
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The WishlistItem identifier")
class WishlistItemResource(Resource):
    """
    WishlistItemResource class

    Allows the manipulation of a single WishlistItem
    GET /wishlists/{wishlist_id}/items/{item_id} - Returns a WishlistItem with the id
    PUT /wishlists/{wishlist_id}/items/{item_id} - Update a WishlistItem with the id
    DELETE /wishlists/{wishlist_id}/items/{item_id} -  Deletes a WishlistItem with the id
    """

    @api.doc("get_wishlist_item")
    @api.response(404, "WishlistItem not found")
    @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """
        Retrieve a single WishlistItem

        This endpoint will return a WishlistItem based on its id
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
            )
        return item.serialize(), status.HTTP_200_OK

    @api.doc("update_wishlist_item")
    @api.response(404, "WishlistItem not found")
    @api.response(400, "The posted WishlistItem data was not valid")
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id):
        """
        Update a WishlistItem

        This endpoint will update a WishlistItem based on the body that is posted
        """
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
            )
        item.deserialize(api.payload)
        item.update()
        return item.serialize(), status.HTTP_200_OK

    @api.doc("delete_wishlist_item")
    @api.response(204, "WishlistItem deleted")
    def delete(self, wishlist_id, item_id):
        """
        Delete a WishlistItem

        This endpoint will delete a WishlistItem based on the id specified in the path
        """
        item = WishlistItem.find(item_id)
        if item:
            item.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{wishlist_id}/items/{item_id}/move-to/{target_wishlist_id}
######################################################################
@api.route("/wishlists/<wishlist_id}/items/<item_id>/move-to/<target_wishlist_id>")
@api.param("wishlist_id", "The source Wishlist identifier")
@api.param("item_id", "The WishlistItem identifier")
@api.param("target_wishlist_id", "The target Wishlist identifier")
class WishlistItemMoveResource(Resource):
    """
    WishlistItemMoveResource class

    Handles moving an item from one wishlist to another
    """

    @api.doc("move_wishlist_item")
    @api.response(404, "WishlistItem or Wishlist not found")
    @api.response(403, "Cannot move item to a wishlist of a different customer")
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id, target_wishlist_id):
        """
        Move an Item from One Wishlist to Another

        This endpoint will move an item from a source wishlist to a target wishlist
        """
        source_wishlist = Wishlist.find(wishlist_id)
        if not source_wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Source wishlist with id '{wishlist_id}' was not found.",
            )
        target_wishlist = Wishlist.find(target_wishlist_id)
        if not target_wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Target wishlist with id '{target_wishlist_id}' was not found.",
            )
        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
            )
        if target_wishlist.customer_id != source_wishlist.customer_id:
            error(status.HTTP_403_FORBIDDEN, "Wishlists belong to different customers.")

        item.wishlist_id = target_wishlist_id
        item.update()
        source_wishlist.items = [i for i in source_wishlist.items if i.id != item_id]
        source_wishlist.update()
        target_wishlist.items.append(item)
        target_wishlist.update()

        return item.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/customers/{customer_id}
######################################################################
@api.route("/wishlists/customers/<customer_id>")
@api.param("customer_id", "The customer identifier")
class WishlistCustomerResource(Resource):
    """
    WishlistCustomerResource class

    Handles deletion of all wishlists for a specific customer
    """

    @api.doc("delete_all_wishlists")
    @api.response(204, "All Wishlists deleted")
    def delete(self, customer_id):
        """
        Delete all wishlists for a specific customer

        This endpoint will delete all wishlists for a specific customer based on the customer id specified in the path
        """
        all_wishlists = Wishlist.find_by_customer_id(customer_id)
        if not all_wishlists:
            return "", status.HTTP_204_NO_CONTENT

        for wishlist in all_wishlists:
            wishlist.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{wishlist_id}/items
######################################################################
@api.route("/wishlists/<wishlist_id>/items")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistItemsDeleteAllResource(Resource):
    """
    WishlistItemsDeleteAllResource class

    Handles deletion of all items in a specific wishlist
    """

    @api.doc("delete_all_wishlist_items")
    @api.response(204, "All WishlistItems deleted")
    def delete(self, wishlist_id):
        """
        Delete all items in a specific wishlist

        This endpoint will delete all items in a specific wishlist based on the wishlist id specified in the path
        """
        all_items = WishlistItem.find_by_wishlist_id(wishlist_id)
        if not all_items:
            return "", status.HTTP_204_NO_CONTENT

        for item in all_items:
            item.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    api.logger.error(reason)
    api.abort(status_code, reason)
