"""
Wishlists Service

This service implements a REST API that allows you to Create, Read, Update
and Delete for managing wishlists and wishlist items on the eCommerce website.
"""

from dateutil import parser
from flask import current_app as app, request
from flask_restx import Resource, reqparse, fields
from service.models import Wishlist, WishlistItem, DataValidationError
from service.common import status  # HTTP Status Codes
from . import api


# Utility functions
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    api.abort(status_code, reason)


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


def validate_wishlist_item_data(data):
    """Validates WishlistItem data"""
    if not data.get("wishlist_id"):
        raise DataValidationError("Invalid WishlistItem: missing or empty wishlist_id")
    if not data.get("product_id"):
        raise DataValidationError("Invalid WishlistItem: missing product_id")


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
                        "added_date": fields.String(
                            description="The date the item was added to the wishlist"
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
        "added_date": fields.String(
            description="The date the item was added to the wishlist"
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
                f"Wishlist with id [{wishlist_id}] could not be found.",
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
                f"Wishlist with id [{wishlist_id}] could not be found.",
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

        check_content_type("application/json")
        wishlist = Wishlist()
        wishlist.deserialize(api.payload)
        wishlist.create()

        app.logger.info("Wishlist with new id [%s] created!", wishlist.id)
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )

        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/<wishlist_id>/items
######################################################################
@api.route("/wishlists/<wishlist_id>/items")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistItemCollection(Resource):
    """
    WishlistItemCollection class

    Allows the manipulation of a single Wishlist Item
    POST /wishlists/{wishlist_id}/items - Add an item to a wishlist
    GET /wishlists/<wishlist_id>/items - List items in a wishlist
    DELETE /wishlists/<wishlist_id>/items - Delete all items from a wishlist
    """

    # ------------------------------------------------------------------
    # LIST ITEMS IN A WISHLIST
    # ------------------------------------------------------------------
    @api.expect(wishlistItem_args, validate=True)
    @api.marshal_list_with(wishlistItem_model)
    def get(self, wishlist_id):
        """
        List all items in a Wishlist

        This endpoint will return all items in a wishlist
        """
        app.logger.info("Request for items in Wishlist with id [%s]", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] could not be found.",
            )

        args = wishlistItem_args.parse_args()
        sort_by = args.get("sort_by")
        order = args.get("order", "asc")

        items = wishlist.items
        if sort_by:
            reverse = order == "desc"
            try:
                if sort_by == "added_date":
                    items = sorted(
                        items,
                        key=lambda x: (
                            parser.parse(x.added_date)
                            if isinstance(x.added_date, str)
                            else x.added_date
                        ),
                        reverse=reverse,
                    )
                else:
                    items = sorted(
                        items, key=lambda x: getattr(x, sort_by), reverse=reverse
                    )
            except AttributeError:
                error(
                    status.HTTP_400_BAD_REQUEST,
                    f"Invalid sort_by parameter: {sort_by}",
                )

        if args.get("price") is not None:
            price = args.get("price")
            items = [item for item in items if item.price <= price]

        results = [item.serialize() for item in items]

        app.logger.info(
            "Returning [%d] items in wishlist [%s]", len(results), wishlist_id
        )

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD AN ITEM TO A WISHLIST
    # ------------------------------------------------------------------
    @api.response(400, "The posted data was not valid")
    @api.expect(create_wishlistItem_model)
    @api.marshal_with(wishlistItem_model, code=201)
    def post(self, wishlist_id):
        """
        Add an item to a Wishlist

        This endpoint will add an item to a wishlist
        """
        app.logger.info("Request to add an item to wishlist with id [%s]", wishlist_id)

        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] could not be found.",
            )

        app.logger.info("Processing: %s", api.payload)

        data = api.payload
        data["wishlist_id"] = wishlist_id
        validate_wishlist_item_data(data)

        item = WishlistItem()
        item.deserialize(data)
        item.create()

        app.logger.info("Item [%s] added to wishlist [%s]", item.id, wishlist_id)
        location_url = api.url_for(
            WishlistItemResource,
            wishlist_id=wishlist_id,
            item_id=item.id,
            _external=True,
        )

        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL ITEMS FROM A WISHLIST
    # ------------------------------------------------------------------
    @api.response(204, "All items deleted")
    def delete(self, wishlist_id):
        """
        Delete all items from a Wishlist

        This endpoint will delete all items from a wishlist
        """
        app.logger.info(
            "Request to delete all items from wishlist with id [%s]", wishlist_id
        )

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] could not be found.",
            )

        for item in wishlist.items:
            item.delete()

        app.logger.info("All items deleted from wishlist [%s]", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


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
    GET /wishlists/{wishlist_id}/items/{item_id} - Returns the item with the id
    PUT /wishlists/{wishlist_id}/items/{item_id} - Update an item with the id
    DELETE /wishlists/{wishlist_id}/items/{item_id} - Deletes an item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.response(404, "Wishlist or Item not found")
    @api.marshal_with(wishlistItem_model)
    def get(self, wishlist_id, item_id):
        """
        Retrieve a single Wishlist Item

        This endpoint will return an item based on its id
        """
        app.logger.info(
            "Request to retrieve item [%s] from wishlist with id [%s]",
            item_id,
            wishlist_id,
        )

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] could not be found.",
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] could not be found in wishlist [{wishlist_id}].",
            )

        app.logger.info("Returning item [%s]", item_id)

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.response(404, "Wishlist or Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(create_wishlistItem_model)
    @api.marshal_with(wishlistItem_model)
    def put(self, wishlist_id, item_id):
        """
        Update a Wishlist Item

        This endpoint will update an item based the body that is posted
        """
        app.logger.info(
            "Request to update item [%s] in wishlist with id [%s]", item_id, wishlist_id
        )

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] could not be found.",
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] could not be found in wishlist [{wishlist_id}].",
            )

        app.logger.info("Processing: %s", api.payload)

        data = api.payload
        data["wishlist_id"] = wishlist_id  # Ensure wishlist_id is correctly set
        validate_wishlist_item_data(data)

        item.deserialize(data)
        item.update()

        app.logger.info("Item [%s] updated in wishlist [%s]", item_id, wishlist_id)

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST ITEM
    # ------------------------------------------------------------------
    @api.response(204, "Item deleted")
    def delete(self, wishlist_id, item_id):
        """
        Delete a Wishlist Item

        This endpoint will delete an item based on its id
        """
        app.logger.info(
            "Request to delete item [%s] from wishlist with id [%s]",
            item_id,
            wishlist_id,
        )

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id [{wishlist_id}] could not be found.",
            )

        item = WishlistItem.find(item_id)
        if item:
            item.delete()

        app.logger.info("Item [%s] deleted from wishlist [%s]", item_id, wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/<wishlist_id>/items/<item_id>/move-to/<target_wishlist_id>
######################################################################
@api.route(
    "/wishlists/<wishlist_id>/items/<item_id>/move-to/<target_wishlist_id>",
    strict_slashes=False,
)
@api.param("wishlist_id", "The Wishlist identifier")
@api.param("item_id", "The Wishlist Item identifier")
@api.param("target_wishlist_id", "The target Wishlist identifier")
class MoveWishlistItemResource(Resource):
    """
    MoveWishlistItemResource class

    Allows moving a single Wishlist Item to another Wishlist
    PUT /wishlists/{wishlist_id}/items/{item_id}/move-to/{target_wishlist_id} - Move the item
    """

    # ------------------------------------------------------------------
    # MOVE A WISHLIST ITEM TO ANOTHER WISHLIST
    # ------------------------------------------------------------------
    @api.response(404, "Wishlist or Item not found")
    @api.response(400, "The posted Item data was not valid")
    def put(self, wishlist_id, item_id, target_wishlist_id):
        """
        Move a Wishlist Item to another Wishlist

        This endpoint will move an item to another wishlist
        """
        app.logger.info(
            "Request to move item [%s] from wishlist [%s] to wishlist [%s]",
            item_id,
            wishlist_id,
            target_wishlist_id,
        )

        source_wishlist = Wishlist.find(wishlist_id)
        if not source_wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Source wishlist with id [{wishlist_id}] could not be found.",
            )

        target_wishlist = Wishlist.find(target_wishlist_id)
        if not target_wishlist:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Target wishlist with id [{target_wishlist_id}] could not be found.",
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] could not be found in source wishlist [{wishlist_id}].",
            )

        if source_wishlist.customer_id != target_wishlist.customer_id:
            error(
                status.HTTP_403_FORBIDDEN,
                "Cannot move item to a wishlist of a different customer.",
            )

        item.wishlist_id = target_wishlist_id
        item.update()

        app.logger.info(
            "Item [%s] moved from wishlist [%s] to wishlist [%s]",
            item_id,
            wishlist_id,
            target_wishlist_id,
        )

        return item.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/customers/<customer_id>
######################################################################
@api.route("/wishlists/customers/<customer_id>")
@api.param("customer_id", "The Customer identifier")
class WishlistCustomerCollection(Resource):
    """Handles deletion of all wishlists for a specific customer"""

    @api.response(204, "All wishlists deleted")
    def delete(self, customer_id):
        """
        Delete all wishlists for a customer

        This endpoint will delete all wishlists associated with a specific customer
        """
        app.logger.info(
            "Request to delete all wishlists for customer [%s]", customer_id
        )

        wishlists = Wishlist.find_by_customer_id(customer_id)
        if not wishlists:
            error(
                status.HTTP_404_NOT_FOUND,
                f"No wishlists found for customer with id [{customer_id}]",
            )

        for wishlist in wishlists:
            wishlist.delete()

        app.logger.info("All wishlists deleted for customer [%s]", customer_id)

        return "", status.HTTP_204_NO_CONTENT
