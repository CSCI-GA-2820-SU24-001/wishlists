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

from flask import current_app as app  # Import Flask application
from flask import request
from flask_restx import Resource, reqparse, fields
from service.models import Wishlist, WishlistItem
from service.common import status  # HTTP Status Codes
from service import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health_check():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


# Swagger data models
wishlist_model = api.model(
    "Wishlist",
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "customer_id": fields.String(
            required=True, description="The customer id of the wishlist owner"
        ),
        "name": fields.String(required=True, description="The name of the wishlist"),
        "items": fields.List(
            fields.Nested(
                api.model(
                    "WishlistItem",
                    {
                        "id": fields.String(
                            readOnly=True,
                            description="The unique id assigned internally by service",
                        ),
                        "product_id": fields.String(
                            required=True, description="The product id of the item"
                        ),
                        "description": fields.String(
                            required=False, description="The description of the item"
                        ),
                        "price": fields.Float(
                            required=True, description="The price of the item"
                        ),
                        "wishlist_id": fields.String(
                            required=True, description="The id of the wishlist"
                        ),
                    },
                )
            )
        ),
    },
)

create_wishlistItem_model = api.model(
    "CreateWishlistItem",
    {
        "product_id": fields.String(
            required=True, description="The product id of the item"
        ),
        "description": fields.String(
            required=False, description="The description of the item"
        ),
        "price": fields.Float(required=True, description="The price of the item"),
    },
)

wishlistItem_model = api.inherit(
    "WishlistItem",
    create_wishlistItem_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "wishlist_id": fields.String(
            required=True, description="The id of the wishlist"
        ),
    },
)

# query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "customer_id",
    type=str,
    location="args",
    required=False,
    help="Customer ID of the Wishlist",
)
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="Name of the Wishlist"
)

wishlistItem_args = reqparse.RequestParser()
wishlistItem_args.add_argument(
    "price", type=float, location="args", required=False, help="Price of the Item"
)
wishlistItem_args.add_argument(
    "sort_by",
    type=str,
    location="args",
    required=False,
    help="Sort items by this field",
)
wishlistItem_args.add_argument(
    "order", type=str, location="args", required=False, help="Sort order: asc or desc"
)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


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

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single Wishlist

        This endpoint will return a Wishlist based on its id
        """
        app.logger.info("Request to retrieve Wishlist with id [%s]", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        app.logger.info("Returning Wishlist with id [%s]", wishlist_id)

        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST
    # ------------------------------------------------------------------
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

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        wishlist.deserialize(api.payload)
        wishlist.id = wishlist_id
        wishlist.update()

        app.logger.info("Wishlist with id [%s] updated!", wishlist_id)

        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------
    @api.response(204, "Wishlist deleted")
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based on its id
        """
        app.logger.info("Request to delete Wishlist with id [%s]", wishlist_id)

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
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """Returns all of the Wishlists"""
        app.logger.info("Request for Wishlists list")

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
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """
        Creates a Wishlist

        This endpoint will create a Wishlist based the data on the body that is posted
        """
        app.logger.info("Request to create a Wishlist")
        app.logger.info("Processing: %s", api.payload)

        wishlist = Wishlist()
        wishlist.deserialize(api.payload)
        wishlist.create()

        app.logger.info("Wishlist with id [%s] saved!", wishlist.id)

        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )

        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/<wishlist_id>/items/<item_id>
######################################################################
@api.route("/wishlists/<wishlist_id>/items/<item_id>")
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
    @api.response(404, "Wishlist Item not found")
    @api.marshal_with(wishlistItem_model)
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

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] was not found in Wishlist [{wishlist_id}].",
            )

        app.logger.info(
            "Returning Item with id [%s] in Wishlist with id [%s]", item_id, wishlist_id
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.response(404, "Wishlist Item not found")
    @api.response(400, "The posted Wishlist Item data was not valid")
    @api.expect(wishlistItem_model)
    @api.marshal_with(wishlistItem_model)
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

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        item = WishlistItem.find(item_id)
        if not item:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] was not found in Wishlist with id [{wishlist_id}].",
            )

        item.deserialize(api.payload)
        item.update()

        app.logger.info(
            "Item with id [%s] in Wishlist with id [%s] updated!", item_id, wishlist_id
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST ITEM
    # ------------------------------------------------------------------
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

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

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
#  PATH: /wishlists/<wishlist_id>/items
######################################################################
@api.route("/wishlists/<wishlist_id>/items", strict_slashes=False)
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistItemCollection(Resource):
    """Handles all interactions with collections of Wishlist Items"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN A WISHLIST
    # ------------------------------------------------------------------
    @api.expect(wishlistItem_args, validate=True)
    @api.marshal_list_with(wishlistItem_model)
    def get(self, wishlist_id):
        """
        Retrieve all Items in a Wishlist
        """
        app.logger.info("Request to list Items in Wishlist with id [%s]", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        args = wishlistItem_args.parse_args()
        price = args.get("price")
        sort_by = args.get("sort_by", "price").lower()
        order = args.get("order", "asc").lower()

        items = wishlist.items
        if price:
            app.logger.info("Filtering by price [%s]", price)
            items = WishlistItem.find_by_price(wishlist_id, price)

        if sort_by == "price":
            app.logger.info("Sorting by price in [%s] order", order)
            items = sorted(
                items, key=lambda item: item.price, reverse=(order == "desc")
            )
        elif sort_by == "added_date":
            app.logger.info("Sorting by added date in [%s] order", order)
            items = sorted(
                items, key=lambda item: item.added_date, reverse=(order == "desc")
            )

        items = [item.serialize() for item in items]

        app.logger.info(
            "Returning [%s] Items in Wishlist with id [%s]", len(items), wishlist_id
        )

        return items, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD AN ITEM TO A WISHLIST
    # ------------------------------------------------------------------
    @api.response(400, "The posted Wishlist Item data was not valid")
    @api.expect(create_wishlistItem_model)
    @api.marshal_with(wishlistItem_model, code=201)
    def post(self, wishlist_id):
        """
        Add an Item in a Wishlist

        This endpoint will create an Item in a Wishlist based on the body that is posted
        """
        app.logger.info("Request to add an Item in Wishlist with id [%s]", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        data = api.payload

        app.logger.info("Processing: %s", data)

        item = WishlistItem.find_by_product_id_wishlist_id(
            data["product_id"], wishlist_id
        )
        if item:
            item.price = data["price"]
            item.update()
        else:
            item = WishlistItem()
            data["wishlist_id"] = wishlist_id
            item.deserialize(data)
            wishlist.items.append(item)
            wishlist.update()

        app.logger.info(
            "Item with id [%s] saved in Wishlist with id [%s]!", item.id, wishlist_id
        )

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
    @api.response(204, "All Wishlist Items deleted")
    def delete(self, wishlist_id):
        """
        Delete all Items in a Wishlist

        This endpoint will delete all Items from a Wishlist based on the id specified in the path
        """
        app.logger.info(
            "Request to delete all Items in Wishlist with id [%s]", wishlist_id
        )

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] was not found.",
            )

        for item in wishlist.items:
            item.delete()

        app.logger.info("Items in Wishlist with id [%s] deleted!", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{source_wishlist_id}/items/{item_id}/move-to/{target_wishlist_id}
######################################################################
@api.route(
    "/wishlists/<source_wishlist_id>/items/<item_id>/move-to/<target_wishlist_id>",
    methods=["PUT"],
)
@api.param("source_wishlist_id", "The source Wishlist identifier")
@api.param("target_wishlist_id", "The target Wishlist identifier")
@api.param("item_id", "The Wishlist Item identifier")
class MoveWishlistItemResource(Resource):
    """Move an Item from One Wishlist to Another"""

    @api.response(404, "Wishlist or Item not found")
    @api.response(403, "Wishlists belong to different customers")
    @api.marshal_with(wishlistItem_model)
    def put(self, source_wishlist_id, item_id, target_wishlist_id):
        """
        Move an Item from One Wishlist to Another

        This endpoint will move an item from a source wishlist to a target wishlist
        """
        app.logger.info(
            "Request to move item with id: %s from wishlist with id: %s to wishlist with id: %s",
            item_id,
            source_wishlist_id,
            target_wishlist_id,
        )

        source_wishlist = Wishlist.find(source_wishlist_id)
        if not source_wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Source wishlist with id '{source_wishlist_id}' could not be found.",
            )

        target_wishlist = Wishlist.find(target_wishlist_id)
        if not target_wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Target wishlist with id '{target_wishlist_id}' could not be found.",
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != source_wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' could not be found in wishlist '{source_wishlist_id}'.",
            )

        if target_wishlist.customer_id != source_wishlist.customer_id:
            error(
                status.HTTP_403_FORBIDDEN,
                "Wishlists belong to different customers.",
            )

        item.wishlist_id = target_wishlist_id
        item.update()

        # Remove the item from source wishlist's items if it is there
        if item in source_wishlist.items:
            source_wishlist.items.remove(item)
        source_wishlist.update()

        target_wishlist.items.append(item)
        target_wishlist.update()

        return item.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/customers/{customer_id}
######################################################################
@api.route("/wishlists/customers/<customer_id>", strict_slashes=False)
@api.param("customer_id", "The Customer identifier")
class CustomerWishlistResource(Resource):
    """Handles deleting all wishlists for a specific customer"""

    @api.response(204, "All Customer Wishlists deleted")
    def delete(self, customer_id):
        """
        Delete all wishlists for a specific customer

        This endpoint will delete all wishlists for specific customer based on the customer id specified in the path
        """
        app.logger.info(
            "Request to delete all wishlists with customer id: %s", customer_id
        )

        all_wishlists = Wishlist.find_by_customer_id(customer_id)
        if not all_wishlists:
            return "", status.HTTP_204_NO_CONTENT

        for wishlist in all_wishlists:
            wishlist.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


# ------------------------------------------------------------------
# Logs error messages before aborting
# ------------------------------------------------------------------
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    api.abort(status_code, reason)


# ------------------------------------------------------------------
# Checks that the media type is correct
# ------------------------------------------------------------------
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )
