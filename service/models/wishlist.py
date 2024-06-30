"""
Models for Wishlists

The models for Wishlists are stored in this module
"""
import logging
from .persistent_base import db, PersistentBase, DataValidationError
from .wishlist_item import WishlistItem
import uuid

logger = logging.getLogger("flask.app")

######################################################################
#  W I S H L I S T    M O D E L
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a Wishlist
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # pylint: disable=invalid-name
    customer_id = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    items = db.relationship("WishlistItem", backref="wishlist", passive_deletes=True)
    def __repr__(self):
        return f"<Wishlist id=[{self.id}]>"

    def serialize(self) -> dict:
        """Converts a Wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "items": [item.serialize() for item in self.items],
        }
        return wishlist

    def deserialize(self, data):
        """
        Populates a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.name = data["name"]

            item_list = data.get("items")
            if item_list:
                for json_item in item_list:
                    item = WishlistItem()
                    item.deserialize(json_item)
                    self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()
