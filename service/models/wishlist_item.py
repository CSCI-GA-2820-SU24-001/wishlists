"""
Models for Wishlists

The models for WishlistItems are stored in this module
"""

import uuid
import logging
from datetime import date
from .persistent_base import db, PersistentBase, DataValidationError

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
    price = db.Column(db.Numeric(), nullable=False)
    added_date = db.Column(db.Date(), nullable=False, default=date.today)
    modified_date = db.Column(
        db.Date(), nullable=False, default=date.today, onupdate=date.today
    )

    def __repr__(self):
        return f"<WishlistItem product_id=[{self.product_id}] wishlist_id=[{self.wishlist_id}]>"

    def __str__(self):
        return f"Product ID: {self.product_id}, Description: {self.description}, Price: {self.price}"

    def serialize(self) -> dict:
        """Converts a WishlistItem into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "description": self.description,
            "price": float(f"{self.price:.2f}"),
            "added_date": self.added_date.isoformat(),
            "modified_date": self.modified_date.isoformat(),
        }

    def deserialize(self, data):
        """
        Populates a WishlistItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if not data.get("wishlist_id"):
                raise DataValidationError("Invalid WishlistItem: missing wishlist_id")
            if not data.get("product_id"):
                raise DataValidationError("Invalid WishlistItem: missing product_id")
            if "price" not in data or not isinstance(data["price"], (int, float)):
                raise DataValidationError(
                    "Invalid WishlistItem: missing or invalid price"
                )

            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.description = data.get("description", "")
            self.price = data["price"]

            # Handle date fields
            if "added_date" in data:
                if isinstance(data["added_date"], str):
                    self.added_date = date.fromisoformat(data["added_date"])
                else:
                    self.added_date = data["added_date"]
            if "modified_date" in data:
                if isinstance(data["modified_date"], str):
                    self.modified_date = date.fromisoformat(data["modified_date"])
                else:
                    self.modified_date = data["modified_date"]

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
    def find_by_price(cls, wishlist_id, price):
        """Returns all WishlistItems with the given wishlist_id and price

        Args:
            wishlist_id (string): the wishlist_id of the WishlistItem you want to match
            price(string): the price of the WishlistItem you want to match
        """
        return cls.query.filter(
            cls.wishlist_id == wishlist_id, cls.price <= float(price)
        ).all()

    @classmethod
    def find_by_wishlist_id(cls, wishlist_id):
        """Returns all items with the given wishlist_id

        Args:
            wishlist_id (string): the wishlist_id of the WishlistItems you want to match
        """
        logger.info("Processing wishlist_id query for %s ...", wishlist_id)
        return cls.query.filter(cls.wishlist_id == wishlist_id).all()

    @classmethod
    def find_by_product_id_wishlist_id(cls, product_id, wishlist_id):
        """Returns a WishlistItem with the given product_id and wishlist_id"""
        logger.info("Processing product_id query for %s", product_id)
        return cls.query.filter(
            cls.product_id == product_id, cls.wishlist_id == wishlist_id
        ).first()
