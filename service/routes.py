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
Wishlists Service

This service implements a REST API that allows you to Create, Read, Update
and Delete for managing wishlists and wishlist items on the eCommerce website
"""

from flask import (
    current_app as app,
    request,
    abort,
)  # Import Flask application and abort
from flask_restx import Resource, reqparse, fields
from service.models import Wishlist, WishlistItem, DataValidationError
from service.common import status  # HTTP Status Codes
from . import api

######################################################################
# Define the models so that the docs reflect what can be sent
######################################################################
create_wishlist_item_model = api.model(
    "WishlistItem",
    {
        "wishlist_id": fields.String(required=True, description="ID of the wishlist"),
        "product_id": fields.String(required=True, description="ID of the product"),
        "description": fields.String(description="Description of the product"),
        "price": fields.Float(required=True, description="Price of the product"),
        "added_date": fields.String(description="Date when the item was added"),
    },
)

wishlist_item_model = api.inherit(
    "WishlistItemModel",
    create_wishlist_item_model,
    {
        "id": fields.String(
            readOnly=True,
            description="The unique ID of the wishlist item assigned internally by the service",
        ),
    },
)

create_wishlist_model = api.model(
    "Wishlist",
    {
        "customer_id": fields.String(required=True, description="ID of the customer"),
        "name": fields.String(required=True, description="Name of the wishlist"),
        "created_date": fields.String(description="Date when the wishlist was created"),
        "items": fields.List(
            fields.Nested(wishlist_item_model),
            required=False,
            description="Items in the wishlist",
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "id": fields.String(
            readOnly=True,
            description="The unique ID of the wishlist assigned internally by the service",
        ),
    },
)


######################################################################
# QUERY STRING ARGUMENTS
######################################################################
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "customer_id",
    type=str,
    location="args",
    required=False,
    help="Customer ID of the wishlist",
)
wishlist_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="Name of the wishlist",
)

wishlist_item_args = reqparse.RequestParser()
wishlist_item_args.add_argument(
    "price",
    type=float,
    location="args",
    required=False,
    help="Price of the items",
)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health_check():
    """Let them know our heart is still beating"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/{id}
######################################################################
@api.route("/wishlists/<string:wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """
    WishlistResource class

    Allows the manipulation of a single Wishlist
    GET /wishlists/{id} - Returns a Wishlist with the id
    PUT /wishlists/{id} - Update a Wishlist with the id
    DELETE /wishlists/{id} -  Deletes a Wishlist with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlists")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist

        This endpoint will return a Wishlist based on its id
        """
        app.logger.info("Request to retrieve Wishlist with id [%s]", wishlist_id)

        # Attempt to find the Wishlist and abort if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        app.logger.info("Returning Wishlist with id [%s]", wishlist_id)

        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST
    # ------------------------------------------------------------------
    @api.doc("update_wishlists")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist

        This endpoint will update a Wishlist based on the body that is posted
        """
        app.logger.info("Request to update Wishlist with id [%s]", wishlist_id)

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        # Update from the json in the body of the request
        wishlist.deserialize(api.payload)
        wishlist.id = wishlist_id
        wishlist.update()

        app.logger.info("Wishlist with id [%s] updated!", wishlist_id)

        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("delete_wishlists")
    @api.response(204, "Wishlist deleted")
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based on its id
        """
        app.logger.info("Request to delete Wishlist with id [%s]", wishlist_id)

        # Attempt to find the Wishlist and abort if not found
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
            app.logger.info("Wishlist with id [%s] deleted!", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists
######################################################################
@api.route("/wishlists", strict_slashes=False)
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists"""

    # ------------------------------------------------------------------
    # LIST ALL WISHLISTS
    # ------------------------------------------------------------------
    @api.doc("list_wishlists")
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """Returns all of the Wishlists"""
        app.logger.info("Request for Wishlist list")

        # Get the query parameters
        args = wishlist_args.parse_args()
        customer_id = args.get("customer_id")
        name = args.get("name")

        wishlists = []
        if customer_id:
            app.logger.info("Filtering by customer ID [%s]", customer_id)
            wishlists = Wishlist.find_by_customer_id(customer_id)
        elif name:
            app.logger.info("Filtering by name [%s]", name)
            wishlists = Wishlist.find_by_name(name)
        else:
            wishlists = Wishlist.all()
            app.logger.info("Returning unfiltered list")
        wishlists = [wishlist.serialize() for wishlist in wishlists]

        app.logger.info("Returning [%d] wishlists", len(wishlists))

        return wishlists, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW WISHLIST
    # ------------------------------------------------------------------
    @api.doc("create_wishlists")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist

        This endpoint will create a Wishlist based on the data in the body that is posted
        """
        app.logger.info("Request to create a Wishlist")
        app.logger.info("Processing: %s", api.payload)

        # Create the wishlist
        wishlist = Wishlist()
        try:
            wishlist.deserialize(api.payload)
        except DataValidationError as e:
            abort(
                status.HTTP_400_BAD_REQUEST,
                str(e),
            )

        wishlist.create()

        app.logger.info("Wishlist with id [%s] saved!", wishlist.id)

        # Return the location of the new item
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )

        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/{id}/items/{id}
######################################################################
@api.route("/wishlists/<string:wishlist_id>/items/<string:item_id>")
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The Wishlist Item identifier")
class WishlistItemResource(Resource):
    """
    WishlistItemResource class

    Allows the manipulation of a single Wishlist Item
    GET /wishlists/{id}/items/{id} - Returns a Wishlist Item with the id
    PUT /wishlists/{id}/items/{id} - Update a Wishlist Item with the id
    DELETE /wishlists/{id}/items/{id} -  Deletes a Wishlist Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM FROM A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlist_items")
    @api.response(404, "Wishlist Item not found")
    @api.marshal_with(wishlist_item_model)
    def get(self, wishlist_id, item_id):
        """
        Retrieve a single Item from Wishlist

        This endpoint will return an Item from Wishlist based on its id
        """
        app.logger.info(
            "Request to Retrieve an Item with id [%s] from Wishlist with id [%s]",
            item_id,
            wishlist_id,
        )

        # Attempt to find the Wishlist and abort if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in Wishlist '{wishlist_id}'.",
            )

        app.logger.info(
            "Returning Item with id [%s] in Wishlist with id [%s]",
            item_id,
            wishlist_id,
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.doc("update_wishlist_items")
    @api.response(404, "Wishlist Item not found")
    @api.response(400, "The posted Wishlist Item data was not valid")
    @api.expect(wishlist_item_model)
    @api.marshal_with(wishlist_item_model)
    def put(self, wishlist_id, item_id):
        """
        Update an Item in a Wishlist

        This endpoint will update an Item in a Wishlist based on the body that is posted
        """
        app.logger.info(
            "Request to update Item with id [%s] in Wishlist with id [%s]",
            item_id,
            wishlist_id,
        )

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        # Attempt to find the item and abort if not found
        item = WishlistItem.find(item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in Wishlist with id '{wishlist_id}'.",
            )

        # Update the item with the new data
        item.deserialize(api.payload)

        # Save the updates to the database
        item.update()

        app.logger.info(
            "Item with id [%s] in Wishlist with id [%s] updated!",
            item_id,
            wishlist_id,
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_wishlist_items")
    @api.response(204, "Wishlist Item deleted")
    def delete(self, wishlist_id, item_id):
        """
        Delete an Item in a Wishlist

        This endpoint will delete an Item based on the id specified in the path
        """
        app.logger.info(
            "Request to delete Item with id [%s] in Wishlist with id [%s]",
            item_id,
            wishlist_id,
        )

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        # See if the item exists and delete it if it does
        item = WishlistItem.find(item_id)
        if item:
            item.delete()
            app.logger.info(
                "Item with id [%s] deleted from Wishlist with id [%s]!",
                item_id,
                wishlist_id,
            )

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{id}/items
######################################################################
@api.route("/wishlists/<string:wishlist_id>/items", strict_slashes=False)
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistItemCollection(Resource):
    """Handles all interactions with collections of Wishlist Items"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("list_wishlist_items")
    @api.expect(wishlist_item_args, validate=True)
    @api.marshal_list_with(wishlist_item_model)
    def get(self, wishlist_id):
        """
        Retrieve all Items in a Wishlist
        """
        app.logger.info("Request to list Items in Wishlist with id [%s]", wishlist_id)

        # Attempt to find the Wishlist and abort if not found
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        # Get the query parameters
        args = wishlist_item_args.parse_args()
        price = args.get("price")

        items = wishlist.items
        if price:
            app.logger.info("Filtering by price [%s]", price)
            items = [item for item in items if item.price <= float(price)]

        items = [item.serialize() for item in items]

        app.logger.info(
            "Returning [%s] Items in Wishlist with id [%s]",
            len(items),
            wishlist_id,
        )

        return items, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD AN ITEM TO A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("create_wishlist_items")
    @api.response(400, "The posted Wishlist Item data was not valid")
    @api.expect(create_wishlist_item_model)
    @api.marshal_with(wishlist_item_model, code=201)
    def post(self, wishlist_id):
        """
        Add an Item to a Wishlist

        This endpoint will create an Item in a Wishlist based on the body that is posted
        """
        app.logger.info("Request to add an Item in Wishlist with id [%s]", wishlist_id)

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        data = api.payload

        app.logger.info("Processing: %s", data)

        item = WishlistItem.find_by_product_id_wishlist_id(
            data["product_id"], wishlist_id
        )
        if item:
            # Update quantity if the item exists in the wishlist
            item.quantity += data["quantity"]
            item.update()
        else:
            # Add a new item if the item does not exist in the wishlist
            item = WishlistItem()
            data["wishlist_id"] = wishlist_id
            item.deserialize(data)
            wishlist.items.append(item)
            wishlist.update()

        app.logger.info(
            "Item with id [%s] saved in Wishlist with id [%s]!", item.id, wishlist_id
        )

        # Return the location of the new item
        location_url = api.url_for(
            WishlistItemResource,
            item_id=item.id,
            wishlist_id=wishlist_id,
            _external=True,
        )

        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL ITEMS IN A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("delete_all_wishlist_items")
    @api.response(204, "All Wishlist Items deleted")
    def delete(self, wishlist_id):
        """
        Delete all Items in a Wishlist

        This endpoint will delete all Items from a Wishlist based on the id specified in the path
        """
        app.logger.info(
            "Request to delete all Items in Wishlist with id [%s]",
            wishlist_id,
        )

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )

        for item in wishlist.items:
            item.delete()
        app.logger.info("Items in Wishlist with id [%s] deleted!", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# DELETE ALL WISHLISTS FOR SPECIFIC CUSTOMER
######################################################################
@api.route("/wishlists/customers/<string:customer_id>", strict_slashes=False)
@api.param("customer_id", "The Customer identifier")
class DeleteAllWishlists(Resource):
    """Handles the deletion of all wishlists for a specific customer"""

    @api.doc("delete_all_wishlists")
    @api.response(204, "All Wishlists deleted")
    def delete(self, customer_id):
        """
        Delete all wishlists for a specific customer

        This endpoint will delete all wishlists for a specific customer based on the customer id specified in the path
        """
        app.logger.info(
            "Request to delete all wishlists for customer id [%s]", customer_id
        )

        # Retrieve the wishlists to delete and delete them if they exist
        wishlists = Wishlist.find_by_customer_id(customer_id)
        if wishlists:
            for wishlist in wishlists:
                wishlist.delete()
            app.logger.info("All wishlists for customer id [%s] deleted!", customer_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# MOVE ITEM TO ANOTHER WISHLIST
######################################################################
@api.route(
    "/wishlists/<string:source_wishlist_id>/items/<string:item_id>/move-to/<string:target_wishlist_id>"
)
@api.param("source_wishlist_id", "The source Wishlist identifier")
@api.param("item_id", "The Wishlist Item identifier")
@api.param("target_wishlist_id", "The target Wishlist identifier")
class MoveWishlistItem(Resource):
    """Handles moving an item from one wishlist to another"""

    @api.doc("move_wishlist_item")
    @api.response(404, "Wishlist or Wishlist Item not found")
    @api.response(400, "The posted data was not valid")
    def put(self, source_wishlist_id, item_id, target_wishlist_id):
        """
        Move an Item from One Wishlist to Another

        This endpoint will move an item from a source wishlist to a target wishlist
        """
        app.logger.info(
            "Request to move item with id [%s] from wishlist with id [%s] to wishlist with id [%s]",
            item_id,
            source_wishlist_id,
            target_wishlist_id,
        )

        # Find the source wishlist
        source_wishlist = Wishlist.find(source_wishlist_id)
        if not source_wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Source wishlist with id '{source_wishlist_id}' could not be found.",
            )

        # Find the target wishlist
        target_wishlist = Wishlist.find(target_wishlist_id)
        if not target_wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Target wishlist with id '{target_wishlist_id}' could not be found.",
            )

        # Find the item
        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != source_wishlist_id:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found in wishlist '{source_wishlist_id}'.",
            )

        # Check if both wishlists belong to the same customer
        if target_wishlist.customer_id != source_wishlist.customer_id:
            abort(
                status.HTTP_403_FORBIDDEN,
                "Wishlists belong to different customers.",
            )

        # Update the item's wishlist_id and save it to the database
        item.wishlist_id = target_wishlist_id
        item.update()

        # Remove the item from the source wishlist
        source_wishlist.items = [i for i in source_wishlist.items if i.id != item_id]
        source_wishlist.update()

        # Add the item to the target wishlist
        target_wishlist.items.append(item)
        target_wishlist.update()

        app.logger.info(
            "Item with id [%s] moved from wishlist [%s] to wishlist [%s]",
            item_id,
            source_wishlist_id,
            target_wishlist_id,
        )

        return item.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )
