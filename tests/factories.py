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
# cspell:ignore userid postalcode
"""
Test Factory to make fake objects for testing
"""
from datetime import date
from factory import Factory, SubFactory, Sequence, Faker, post_generation
from factory.fuzzy import FuzzyFloat, FuzzyDate
from service.models import Wishlist, WishlistItem


class WishlistFactory(Factory):
    """Creates fake Wishlists"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Wishlist

    id = Sequence(lambda n: f"{n:04d}")
    customer_id = Sequence(lambda n: f"Customer{n:04d}")
    name = Faker("word")
    created_date = FuzzyDate(start_date=date(2000, 1, 1))
    modified_date = FuzzyDate(start_date=date(2000, 1, 1))

    @post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class WishlistItemFactory(Factory):
    """Creates fake WishlistItems"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = WishlistItem

    id = Sequence(lambda n: f"{n:04d}")
    wishlist_id = None  # This can be assigned dynamically if needed
    product_id = Sequence(lambda n: f"{n:04d}")
    description = Faker("sentence")
    price = FuzzyFloat(1.0, 100.0)
    added_date = FuzzyDate(start_date=date(2000, 1, 1))
    modified_date = FuzzyDate(start_date=date(2000, 1, 1))
    wishlist = SubFactory(WishlistFactory)

    @post_generation
    def set_wishlist_id(self, create, extracted, **kwargs):
        """Ensures wishlist_id is set correctly"""
        if self.wishlist and self.wishlist.id:
            self.wishlist_id = self.wishlist.id
