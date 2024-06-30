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
Pet Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Pets from the inventory of pets in the PetShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, WishlistItem
from service.common import status  # HTTP Status Codes


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
                    "url": "/wishlists/{id}/items/{id}",
                    "description": "Read an item in a wishlist",
                },
                {
                    "method": "PUT",
                    "url": "/wishlists/{id}/items/{id}",
                    "description": "Update an item in a wishlist",
                },
                {
                    "method": "DELETE",
                    "url": "/wishlists/{id}/items/{id}",
                    "description": "Delete an item in a wishlist",
                },
            ],
        },
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create an Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create an Wishlist")
    check_content_type("application/json")

    # Create the wishlist
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()
    location_url = "Unimplemented"

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Returns all of the Wishlists"""
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

    This endpoint will update a Wishlist based on the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found."
        )

    # Update from the json in the body of the request
    wishlist.deserialize(request.get_json())
    wishlist.wishlist_id = wishlist_id
    wishlist.update()

    return jsonify(wishlist.serialize()), status.HTTP_200_OK



######################################################################
# DELETE A  WISHLIST
######################################################################

@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based on the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    # Retrieve the wishlist to delete and delete it if it exists
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

    return "", status.HTTP_204_NO_CONTENT



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
