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
from service.models import Wishlist, WishlistItem, DataValidationError
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
    return app.send_static_file("index.html")


######################################################################
# CREATE A WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Create a Wishlist
    This endpoint will create an Wishlist based the data in the body that is posted
    """
    check_content_type("application/json")

    # Check if the wishlist already exists
    wishlist = Wishlist()
    try:
        wishlist.deserialize(request.get_json())
    except DataValidationError as e:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"{e}",
        )
    # if wishlist.find_by_name(wishlist.name):
    #     return jsonify({"name": wishlist.name, "status": "Wishlist already exists."}), status.HTTP_409_CONFLICT

    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()
    location_url = url_for("read_wishlists", wishlist_id=wishlist.id, _external=True)
    app.logger.info(f"Request to create an Wishlist: {message['id']}")

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
    app.logger.info("Request to list wishlists ")
    customer_id = request.args.get("customer_id")
    name = request.args.get("name")

    if customer_id:
        app.logger.info("Filter by customer_id")
        wishlists = Wishlist.find_by_customer_id(customer_id)
    elif name:
        app.logger.info("Filter by name")
        wishlists = Wishlist.find_by_name(name)
    else:
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
        return "", status.HTTP_204_NO_CONTENT

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
    try:
        item.deserialize(request.get_json())
    except DataValidationError as e:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"{e}",
        )

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
    """Returns all of the .filtered items for an Wishlist in given sorting order"""
    app.logger.info("Request for list items for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Get the items for the wishlist
    price = request.args.get("price")
    if price:
        app.logger.info("Find by price: %s", price)
        wishlist.items = WishlistItem.find_by_price(wishlist_id, price)

    app.logger.info("Request to sort items for Wishlist with id: %s", wishlist_id)

    sort_by = request.args.get("sort_by", "price").lower()

    if sort_by == "price":
        # Sort the items by price
        sort_order = request.args.get("order", "asc").lower()
        app.logger.info("Sort by price in %s order", sort_order)

        if sort_order == "desc":
            sorted_items = sorted(
                wishlist.items, key=lambda item: item.price, reverse=True
            )
        else:
            sorted_items = sorted(wishlist.items, key=lambda item: item.price)
    elif sort_by == "added_date":
        # Sort the items by price
        sort_order = request.args.get("order", "desc").lower()
        app.logger.info("Sort by added_date in %s order", sort_order)

        if sort_order == "asc":
            sorted_items = sorted(wishlist.items, key=lambda item: item.added_date)
        else:
            sorted_items = sorted(
                wishlist.items, key=lambda item: item.added_date, reverse=True
            )

    results = [item.serialize() for item in sorted_items]

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
        return {}, status.HTTP_204_NO_CONTENT

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


@app.route(
    "/wishlists/<string:source_wishlist_id>/items/<string:item_id>/move-to/<string:target_wishlist_id>",
    methods=["PUT"],
)
def move_item_to_another_wishlist(source_wishlist_id, item_id, target_wishlist_id):
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
    check_content_type("application/json")

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

    return jsonify(item.serialize()), status.HTTP_200_OK


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


######################################################################
# DELETE ALL WISHLISTS FOR SPECIFIC CUSTOMER
######################################################################
@app.route("/wishlists/customers/<customer_id>", methods=["DELETE"])
def delete_all_wishlists(customer_id):
    """
    Delete all wishlists for a specific customer

    This endpoint will delete all wishlists for specific customer based on the customer id specified in the path
    """
    app.logger.info("Request to delete all wishlist with customer id: %s", customer_id)

    # Retrieve the wishlist to delete and delete it if it exists
    all_wishlists = Wishlist.find_by_customer_id(customer_id)
    if not all_wishlists:
        return "", status.HTTP_204_NO_CONTENT

    for wishlist in all_wishlists:
        wishlist.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# DELETE ALL ITEMS FOR A SPECIFIC WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>/items", methods=["DELETE"])
def delete_all_items(wishlist_id):
    """
    Delete all items in a specific wishlist

    This endpoint will delete all items in a specific wishlist based on the wishlist id specified in the path
    """
    app.logger.info("Request to delete all items with wishlist id: %s", wishlist_id)

    # Retrieve the item to delete and delete it if it exists
    all_items = WishlistItem.find_by_wishlist_id(wishlist_id)
    if not all_items:
        return "", status.HTTP_204_NO_CONTENT

    for item in all_items:
        item.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# HEALTH CHECK ENDPOINT
######################################################################


@app.route("/health", methods=["GET"])
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK
