"""
Test Factory to make fake objects for testing
"""

import factory
from factory import post_generation
import uuid
from service.models import Wishlist



class WishlistFactory(factory.Factory):
    """Creates fake wishlist for tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlist

    wishlist_id = str(uuid.uuid4())
    customer_id = str(uuid.uuid4())
    name = factory.Faker("first_name")
    items = []

    @post_generation
    def wishlist_items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the wishlist_items list"""
        if not create:
            return

        if extracted:
            self.items = extracted

    # Todo: Add your other attributes here...
