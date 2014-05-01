import datetime
import factory
import uuid

from apps.fund.models import Donation, Order
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory


def random_order_number(length=30):
    return unicode(uuid.uuid4().hex)[0:length]


class OrderFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Order

    user = factory.SubFactory(BlueBottleUserFactory)
    order_number = factory.LazyAttribute(lambda t: random_order_number())


class DonationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Donation

    user = factory.SubFactory(BlueBottleUserFactory)
    amount = 20
    project = factory.SubFactory(OnePercentProjectFactory)
    order = factory.SubFactory(OrderFactory)
