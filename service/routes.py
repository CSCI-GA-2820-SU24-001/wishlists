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
from service.models import YourResourceModel
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """ Root URL response """
    return (
        {
            "service name": "Wishlists Service",
            "version": "1.0.0",
            "endpoints": [
                {
                    "method": "GET",
                    "url": "/wishlists",
                    "description": "List all wishlists"
                },
                {
                    "method": "POST",
                    "url": "/wishlists",
                    "description": "Create a wishlist"
                },
                {
                    "method": "GET",
                    "url": "/wishlists/{id}",
                    "description": "Read a wishlist"
                },
                {
                    "method": "PUT",
                    "url": "/wishlists/{id}",
                    "description": "Update a wishlist"
                },
                {
                    "method": "DELETE",
                    "url": "/wishlists/{id}",
                    "description": "Delete a wishlist"
                },
                {
                    "method": "GET",
                    "url": "/wishlists/{id}/items",
                    "description": "List all items in a wishlist"
                },
                {
                    "method": "POST",
                    "url": "/wishlists/{id}/items",
                    "description": "Create an item in a wishlist"
                },
                {
                    "method": "GET",
                    "url": "/wishlists/{id}/items/{id}",
                    "description": "Read an item in a wishlist"
                },
                {
                    "method": "PUT",
                    "url": "/wishlists/{id}/items/{id}",
                    "description": "Update an item in a wishlist"
                },
                {
                    "method": "DELETE",
                    "url": "/wishlists/{id}/items/{id}",
                    "description": "Delete an item in a wishlist"
                }
            ]
        },
        status.HTTP_200_OK
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...
