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

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, WishlistItem
from service.common import status  # HTTP Status Codes


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root URL response"""
    return (
        {
            "service name": "Wishlists Service",
            "version": "1.0.0",
            "endpoints": [
                {
                    "method": "GET",
                    "url": "/wishlists",
                    "description": "List all wishlists",
                },
                {
                    "method": "POST",
                    "url": "/wishlists",
                    "description": "Create a wishlist",
                },
                {
                    "method": "GET",
                    "url": "/wishlists/{id}",
                    "description": "Read a wishlist",
                },
                {
                    "method": "PUT",
                    "url": "/wishlists/{id}",
                    "description": "Update a wishlist",
                },
                {
                    "method": "DELETE",
                    "url": "/wishlists/{id}",
                    "description": "Delete a wishlist",
                },
                {
                    "method": "GET",
                    "url": "/wishlists/{id}/items",
                    "description": "List all items in a wishlist",
                },
                {
                    "method": "POST",
                    "url": "/wishlists/{id}/items",
                    "description": "Create an item in a wishlist",
                },
                {
                    "method": "GET",
                    "url": "/wishlists/{id}/items/{item_id}",
                    "description": "Read an item in a wishlist",
                },
                {
                    "method": "PUT",
                    "url": "/wishlists/{id}/items/{item_id}",
                    "description": "Update an item in a wishlist",
                },
                {
                    "method": "DELETE",
                    "url": "/wishlists/{id}/items/{item_id}",
                    "description": "Delete an item in a wishlist",
                },
            ],
        },
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Create a Wishlist
    This endpoint will create an Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create an Wishlist")
    check_content_type("application/json")

    # Check if the wishlist already exists
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())

    if wishlist.find_by_name(wishlist.name):
        return jsonify({"name": wishlist.name, "status": "Wishlist already exists."}), status.HTTP_409_CONFLICT

    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()
    location_url = url_for("read_wishlists", wishlist_id=wishlist.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ A WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>", methods=["GET"])
def read_wishlists(wishlist_id):
    """
    Read a Wishlist

    This endpoint will read a Wishlist with specified id
    """
    app.logger.info("Request to read a wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )
    result = wishlist.serialize()

    return jsonify(result), status.HTTP_200_OK


######################################################################
# LIST ALL WISHLISTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """
    List all of the Wishlists

    This endpoint will list all of the Wishlists
    """
    app.logger.info("Request for Wishlist list")
    wishlists = Wishlist.all()

    # Return as an array of dictionaries
    results = [wishlist.serialize() for wishlist in wishlists]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING WISHLIST
#######################################################################
@app.route("/wishlists/<string:wishlist_id>", methods=["PUT"])
def update_wishlist(wishlist_id):
    """
    Update a Wishlist

    This endpoint will update a Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # Update from the json in the body of the request
    wishlist.deserialize(request.get_json())
    wishlist.wishlist_id = wishlist_id
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based on the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    # Retrieve the wishlist to delete and delete it if it exists
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        return "", status.HTTP_404_NOT_FOUND

    wishlist.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# ADD AN ITEM TO A WISHLIST
######################################################################
@app.route("/wishlists/<wishlist_id>/items", methods=["POST"])
def create_items(wishlist_id):
    """
    Create an Item in a Wishlist

    This endpoint will add an item to a wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create an Item for Wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Create an item from the json data
    item = WishlistItem()
    item.deserialize(request.get_json())

    # Append the item to the wishlist
    wishlist.items.append(item)
    wishlist.update()

    # Prepare a message to return
    message = item.serialize()

    # Send the location to GET the new item
    location_url = url_for(
        "read_wishlist_item", wishlist_id=wishlist.id, item_id=item.id, _external=True
    )

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ AN ITEM IN A WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>/items/<string:item_id>", methods=["GET"])
def read_wishlist_item(wishlist_id, item_id):
    """
    Read an Item in a Wishlist

    This endpoint will return a Wishlist item based on its id within the specified wishlist
    """
    app.logger.info(
        "Request to read item with id: %s in wishlist with id: %s", item_id, wishlist_id
    )

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )

    # Find the item within the wishlist and abort if it doesn't exist
    item = WishlistItem.find(item_id)
    if not item or item.wishlist_id != wishlist_id:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found in wishlist '{wishlist_id}'.",
        )

    result = item.serialize()
    return jsonify(result), status.HTTP_200_OK


######################################################################
# LIST ITEMS IN A WISHLIST
######################################################################
@app.route("/wishlists/<wishlist_id>/items", methods=["GET"])
def list_items(wishlist_id):
    """Returns all of the items for an Wishlist"""
    app.logger.info("Request for all items for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Get the items for the wishlist
    results = [item.serialize() for item in wishlist.items]

    return jsonify(results), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/wishlists/<wishlist_id>/items/<item_id>", methods=["DELETE"])
def delete_items(wishlist_id, item_id):
    """
    Delete an Item in a Wishlist

    This endpoint will delete an Item based on the id specified in the path
    """
    app.logger.info(
        "Request to delete Item %s for Wishlist id: %s", (wishlist_id, item_id)
    )

    # See if the item exists and delete it if it does
    item = WishlistItem.find(item_id)
    if not item:
        return {}, status.HTTP_404_NOT_FOUND

    item.delete()
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE A WISHLIST ITEM
######################################################################
@app.route("/wishlists/<string:wishlist_id>/items/<string:item_id>", methods=["PUT"])
def update_wishlist_item(wishlist_id, item_id):
    """
    Update an Item in a Wishlist

    This endpoint will update a WishlistItem based on the body that is posted
    """
    app.logger.info(
        "Request to update WishlistItem %s for Wishlist id: %s", item_id, wishlist_id
    )
    check_content_type("application/json")

    # See if the wishlist item exists and abort if it doesn't
    wishlist_item = WishlistItem.find(item_id)
    if not wishlist_item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"WishlistItem with id '{item_id}' could not be found.",
        )

    # Update from the json in the body of the request
    wishlist_item.deserialize(request.get_json())
    wishlist_item.id = item_id
    wishlist_item.update()

    return jsonify(wishlist_item.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if (
        "Content-Type" not in request.headers
    ):  # TODO: cannot cover with tests, since flask sets default Content-type parameter
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
