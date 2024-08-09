"""
Routes for the Wishlist Microservice
This module handles the REST API for managing wishlists and their items.
"""

from flask import jsonify
from flask_restx import Resource, fields
from service.models import Wishlist, WishlistItem
from service.common import status
from . import api

# Define the models used for marshalling
item_model = api.model(
    "WishlistItem",
    {
        "id": fields.String(
            readOnly=True, description="The unique id of the wishlist item"
        ),
        "wishlist_id": fields.String(
            required=True, description="The id of the wishlist"
        ),
        "product_id": fields.String(required=True, description="The id of the product"),
        "description": fields.String(description="Description of the product"),
        "price": fields.Float(required=True, description="Price of the product"),
        "added_date": fields.Date(description="Date when the item was added"),
    },
)

wishlist_model = api.model(
    "Wishlist",
    {
        "id": fields.String(readOnly=True, description="The unique id of the wishlist"),
        "customer_id": fields.String(
            required=True, description="The id of the customer"
        ),
        "name": fields.String(required=True, description="The name of the wishlist"),
        "created_date": fields.Date(description="The date the wishlist was created"),
        "modified_date": fields.Date(
            description="The date the wishlist was last modified"
        ),
        "items": fields.List(
            fields.Nested(item_model), description="The items in the wishlist"
        ),
    },
)


@api.route("/wishlists")
class WishlistCollection(Resource):
    """Handles all operations for creating and listing wishlists"""

    @api.marshal_list_with(wishlist_model)
    def get(self):
        """List all wishlists"""
        wishlists = Wishlist.all()
        return wishlists, status.HTTP_200_OK

    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model, code=status.HTTP_201_CREATED)
    def post(self):
        """Create a new wishlist"""
        data = api.payload
        wishlist = Wishlist()
        wishlist.deserialize(data)
        wishlist.create()
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True
        )
        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


@api.route("/wishlists/<string:wishlist_id>")
class WishlistResource(Resource):
    """Handles operations for a single wishlist"""

    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """Read a wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        return wishlist.serialize(), status.HTTP_200_OK

    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """Update an existing wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        data = api.payload
        wishlist.deserialize(data)
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK

    def delete(self, wishlist_id):
        """Delete a wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
        return "", status.HTTP_204_NO_CONTENT


@api.route("/wishlists/<string:wishlist_id>/items")
class WishlistItemCollection(Resource):
    """Handles operations for managing items in a wishlist"""

    @api.marshal_list_with(item_model)
    def get(self, wishlist_id):
        """List all items in a wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        return wishlist.items, status.HTTP_200_OK

    @api.expect(item_model)
    @api.marshal_with(item_model, code=status.HTTP_201_CREATED)
    def post(self, wishlist_id):
        """Add an item to a wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        data = api.payload
        item = WishlistItem()
        item.deserialize(data)
        wishlist.items.append(item)
        wishlist.update()
        location_url = api.url_for(
            WishlistItemResource,
            wishlist_id=wishlist_id,
            item_id=item.id,
            _external=True,
        )
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


@api.route("/wishlists/<string:wishlist_id>/items/<string:item_id>")
class WishlistItemResource(Resource):
    """Handles operations for a single wishlist item"""

    @api.marshal_with(item_model)
    def get(self, wishlist_id, item_id):
        """Read an item in a wishlist"""
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' was not found.",
            )
        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != wishlist_id:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
            )
        return item.serialize(), status.HTTP_200_OK

    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, wishlist_id, item_id):
        """Update an item in a wishlist"""
        item = WishlistItem.find(item_id)
        if not item:
            api.abort(
                status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found."
            )
        data = api.payload
        item.deserialize(data)
        item.update()
        return item.serialize(), status.HTTP_200_OK

    def delete(self, wishlist_id, item_id):
        """Delete an item in a wishlist"""
        item = WishlistItem.find(item_id)
        if item:
            item.delete()
        return "", status.HTTP_204_NO_CONTENT


@api.route(
    "/wishlists/<string:source_wishlist_id>/items/<string:item_id>/move-to/<string:target_wishlist_id>"
)
class MoveWishlistItemResource(Resource):
    """Handles moving an item from one wishlist to another"""

    @api.marshal_with(item_model)
    def put(self, source_wishlist_id, item_id, target_wishlist_id):
        """Move an item from one wishlist to another"""
        source_wishlist = Wishlist.find(source_wishlist_id)
        if not source_wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Source wishlist with id '{source_wishlist_id}' could not be found.",
            )

        target_wishlist = Wishlist.find(target_wishlist_id)
        if not target_wishlist:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Target wishlist with id '{target_wishlist_id}' could not be found.",
            )

        if target_wishlist.customer_id != source_wishlist.customer_id:
            api.abort(
                status.HTTP_403_FORBIDDEN, "Wishlists belong to different customers."
            )

        item = WishlistItem.find(item_id)
        if not item or item.wishlist_id != source_wishlist_id:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found in wishlist '{source_wishlist_id}'.",
            )

        item.wishlist_id = target_wishlist_id
        item.update()

        return item.serialize(), status.HTTP_200_OK


@api.route("/health")
class HealthCheckResource(Resource):
    """Health Check Endpoint"""

    def get(self):
        """Let them know our heart is still beating"""
        return jsonify(status=200, message="Healthy"), status.HTTP_200_OK
