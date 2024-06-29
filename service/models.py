"""
Models for Wishlist Service

All of the models are stored in this module
"""

import logging
import uuid
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    __tablename__ = 'customers'

    customer_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    
    # One-to-many relationship with Wishlist
    wishlists = db.relationship('Wishlist', backref='customer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.name} id=[{self.customer_id}]>"

    def create(self):
        """Creates a Customer to the database"""
        logger.info("Creating %s", self.name)
        self.customer_id = str(uuid.uuid4())
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates a Customer to the database"""
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {"customer_id": self.customer_id, "name": self.name}

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid Customer: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError("Invalid Customer: body of request contained bad or no data " + str(error)) from error
        return self

    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Customers with the given name"""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()


class Wishlist(db.Model):
    """
    Class that represents a Wishlist
    """

    __tablename__ = 'wishlists'

    wishlist_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.customer_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    
    # One-to-many relationship with WishlistItem
    items = db.relationship('WishlistItem', backref='wishlist', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.wishlist_id}]>"

    def create(self):
        """Creates a Wishlist to the database"""
        logger.info("Creating %s", self.name)
        self.wishlist_id = str(uuid.uuid4())
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates a Wishlist to the database"""
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Wishlist from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Wishlist into a dictionary"""
        return {"wishlist_id": self.wishlist_id, "customer_id": self.customer_id, "name": self.name}

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.name = data["name"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid Wishlist: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError("Invalid Wishlist: body of request contained bad or no data " + str(error)) from error
        return self

    @classmethod
    def all(cls):
        """Returns all of the Wishlists in the database"""
        logger.info("Processing all Wishlists")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Wishlist by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Wishlists with the given name"""
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()


class WishlistItem(db.Model):
    """
    Class that represents a WishlistItem
    """

    __tablename__ = 'wishlist_items'

    item_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wishlist_id = db.Column(db.String(36), db.ForeignKey('wishlists.wishlist_id'), nullable=False)
    product_id = db.Column(db.String(36), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<WishlistItem {self.description} id=[{self.item_id}]>"

    def create(self):
        """Creates a WishlistItem to the database"""
        logger.info("Creating %s", self.description)
        self.item_id = str(uuid.uuid4())
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates a WishlistItem to the database"""
        logger.info("Saving %s", self.description)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a WishlistItem from the data store"""
        logger.info("Deleting %s", self.description)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a WishlistItem into a dictionary"""
        return {
            "item_id": self.item_id,
            "wishlist_id": self.wishlist_id,
            "product_id": self.product_id,
            "description": self.description,
            "price": str(self.price),
        }

    def deserialize(self, data):
        """
        Deserializes a WishlistItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.product_id = data["product_id"]
            self.description = data["description"]
            self.price = data["price"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid WishlistItem: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError("Invalid WishlistItem: body of request contained bad or no data " + str(error)) from error
        return self

    @classmethod
    def all(cls):
        """Returns all of the WishlistItems in the database"""
        logger.info("Processing all WishlistItems")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a WishlistItem by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_wishlist(cls, wishlist_id):
        """Returns all WishlistItems for a given wishlist"""
        logger.info("Processing wishlist_id query for %s ...", wishlist_id)
        return cls.query.filter(cls.wishlist_id == wishlist_id).all()


