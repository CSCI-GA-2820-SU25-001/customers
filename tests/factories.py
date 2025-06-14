"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Customer


class CustomerFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Customer

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    address = factory.Faker("address")
    email = factory.Faker("email")

