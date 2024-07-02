"""
Models for Wishlist

All of the models are stored in this package
"""

from .persistent_base import db, DataValidationError
from .wishlist_item import WishlistItem
from .wishlist import Wishlist
