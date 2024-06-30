"""
Models for Wishlists

The models for WishlistItems are stored in this module
"""

from .persistent_base import db, logger, PersistentBase, DataValidationError
import uuid


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

    def __repr__(self):
        return f"<WishlistItem product_id=[{self.product_id}] wishlist_id=[{self.wishlist_id}]>"

    def __str__(self):
        return (
            f"Product ID: {self.product_id}, Description: {self.description}, Price: {self.price}"
        )

    def serialize(self) -> dict:
        """Converts a WishlistItem into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "description": self.description,
            "price": float(self.price),
        }

    def deserialize(self, data):
        """
        Populates a WishlistItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.description = data.get("description", "")

            if isinstance(data["price"], (int, float)):
                self.price = data["price"]
            else:
                raise TypeError(
                    "Invalid type for int/float [price]: "
                    + str(type(data["price"]))
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

    ##################################################
    # Class Methods
    ##################################################

    @classmethod
    def find_by_wishlist_id(cls, wishlist_id):
        """Returns all WishlistItems with the given wishlist_id

        Args:
            wishlist_id (string): the wishlist_id of the WishlistItem you want to match
        """
        logger.info("Processing wishlist_id query for %s ...", wishlist_id)
        return cls.query.filter(cls.wishlist_id == wishlist_id).all()

    @classmethod
    def find_by_product_id(cls, product_id):
        """Returns all WishlistItems with the given product_id

        Args:
            product_id (string): the product_id of the WishlistItem you want to match
        """
        logger.info("Processing product_id query for %s", product_id)
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_product_id_wishlist_id(cls, product_id, wishlist_id):
        """Returns all WishlistItems with the given product_id and wishlist_id

        Args:
            product_id (string): the product_id of the WishlistItem you want to match
            wishlist_id (string): the wishlist_id of the WishlistItem you want to match
        """
        logger.info("Processing product_id query for %s", product_id)
        return cls.query.filter(cls.product_id == product_id, cls.wishlist_id == wishlist_id).all()

    @classmethod
    def find_by_description(cls, description):
        """Returns all WishlistItems with the given description

        Args:
            description (string): the description of the WishlistItem you want to match
        """
        logger.info("Processing description query for %s ...", description)
        return cls.query.filter(cls.description == description).all()
