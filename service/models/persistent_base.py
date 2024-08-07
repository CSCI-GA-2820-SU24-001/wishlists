"""
Persistent Base class for database CRUD functions
"""

import logging
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DataError

logger = logging.getLogger("flask.app")

db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for any data validation errors when deserializing"""


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self) -> None:
        """
        Creates a Wishlist/Wishlist Item in the database
        """
        logger.info("Creating %s", self)
        try:
            db.session.add(self)
            db.session.commit()
        except DataError as e:
            db.session.rollback()
            logger.error("DataError creating record: %s", self)
            raise DataValidationError(e.orig) from e
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a Wishlist/Wishlist Item in the database
        """
        logger.info("Updating %s", self)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except DataError as e:
            db.session.rollback()
            logger.error("DataError updating record: %s", self)
            raise DataValidationError(e.orig) from e
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self) -> None:
        """Removes a Wishlist/Wishlist Item from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except DataError as e:
            db.session.rollback()
            logger.error("DataError deleting record: %s", self)
            raise DataValidationError(e.orig) from e
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        # pylint: disable=no-member
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        # pylint: disable=no-member
        return db.session.get(cls, by_id)
