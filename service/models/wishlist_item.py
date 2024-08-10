"""
Models for Wishlists

The models for WishlistItems are stored in this module
"""

import uuid
import logging
from datetime import date
from .persistent_base import db, PersistentBase, DataValidationError
from sqlalchemy import func

logger = logging.getLogger("flask.app")

######################################################################
#  W I S H L I S T   I T E M   M O D E L
######################################################################


class WishlistItem(db.Model, PersistentBase):
    """
    Class that represents a WishlistItem
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wishlist_id = db.Column(
        db.String(36), db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(db.String(36), nullable=False)
    description = db.Column(db.String(256))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    added_date = db.Column(db.Date(), nullable=False, default=date.today())
    modified_date = db.Column(
        db.Date(), nullable=False, default=date.today(), onupdate=date.today()
    )

    def __repr__(self):
        return (
            f"<WishlistItem: item_id: {self.id}, product_id={self.product_id}, Description: {self.description}, "
            + f"Price: {self.price},  wishlist_id={self.wishlist_id}, "
            + f"added_date: {self.added_date}, modified_date: {self.modified_date}>"
        )

    def __str__(self):
        return (
            f"Product ID: : item_id: {self.id}, product_id={self.product_id}, Description: {self.description}, "
            + f"Price: {self.price},  wishlist_id={self.wishlist_id}, "
            + f"added_date: {self.added_date}, modified_date: {self.modified_date}>"
        )

    def serialize(self) -> dict:
        """Converts a WishlistItem into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "description": self.description,
            "price": round(float(self.price), 2),
            "added_date": self.added_date,
            "modified_date": self.modified_date,
        }

    def deserialize(self, data):
        """
        Populates a WishlistItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if data["wishlist_id"] == "":
                raise DataValidationError("Invalid Wishlist: missing wishlist_id")

            if data["product_id"] == "":
                raise DataValidationError("Invalid Wishlist: missing product_id")

            # self.added_date = date.today()
            # self.modified_date = date.today()
            # if data["added_date"]:
            #     self.added_date = data["added_date"]
            # if data["modified_date"]:
            #     self.modified_date = data["modified_date"]

            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.description = data.get("description", "")

            if isinstance(data["price"], (int, float)):
                self.price = round(float(data["price"]), 2)
            else:
                raise TypeError(
                    "Invalid type for int/float [price]: " + str(type(data["price"]))
                )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid WishlistItem: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid WishlistItem: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    @classmethod
    def find_by_price(cls, wishlist_id, price):
        """Returns all WishlistItems with the given wishlist_id and price

        Args:
            wishlist_id (string): the wishlist_id of the WishlistItem you want to match
            price(string): the price of the WishlistItem you want to match
        """

        return cls.query.filter(
            cls.wishlist_id == wishlist_id,
            func.round(cls.price, 2) <= round(float(price), 2),
        ).all()

    @classmethod
    def find_by_wishlist_id(cls, wishlist_id):
        """Returns all items with the given wishlist_id

        Args:
            wishlist_id (string): the wishlist_id of the WishlistItems you want to match
        """
        logger.info("Processing wishlist_id query for %s ...", wishlist_id)
        return cls.query.filter(cls.wishlist_id == wishlist_id).all()

    ##################################################
    # Class Methods
    ##################################################

    # @classmethod
    # def find_by_wishlist_id(cls, wishlist_id):
    #     """Returns all WishlistItems with the given wishlist_id

    #     Args:
    #         wishlist_id (string): the wishlist_id of the WishlistItem you want to match
    #     """
    #     logger.info("Processing wishlist_id query for %s ...", wishlist_id)
    #     return cls.query.filter(cls.wishlist_id == wishlist_id).all()

    # @classmethod
    # def find_by_product_id(cls, product_id):
    #     """Returns all WishlistItems with the given product_id

    #     Args:
    #         product_id (string): the product_id of the WishlistItem you want to match
    #     """
    #     logger.info("Processing product_id query for %s", product_id)
    #     return cls.query.filter(cls.product_id == product_id).all()

    # @classmethod
    # def find_by_product_id_wishlist_id(cls, product_id, wishlist_id):
    #     """Returns all WishlistItems with the given product_id and wishlist_id

    #     Args:
    #         product_id (string): the product_id of the WishlistItem you want to match
    #         wishlist_id (string): the wishlist_id of the WishlistItem you want to match
    #     """
    #     logger.info("Processing product_id query for %s", product_id)
    #     return cls.query.filter(cls.product_id == product_id, cls.wishlist_id == wishlist_id).all()

    # @classmethod
    # def find_by_description(cls, description):
    #     """Returns all WishlistItems with the given description

    #     Args:
    #         description (string): the description of the WishlistItem you want to match
    #     """
    #     logger.info("Processing description query for %s ...", description)
    #     return cls.query.filter(cls.description == description).all()
