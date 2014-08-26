import datetime
from bluebottle.utils.model_dispatcher import get_donation_model, get_order_model
import factory
import uuid

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory

DONATION_MODEL = get_donation_model()
ORDER_MODEL = get_order_model()


def random_order_number(length=30):
    return unicode(uuid.uuid4().hex)[0:length]


class OrderFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ORDER_MODEL

    user = factory.SubFactory(BlueBottleUserFactory)
    order_number = factory.LazyAttribute(lambda t: random_order_number())


class DonationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DONATION_MODEL

    user = factory.SubFactory(BlueBottleUserFactory)
    amount = 20
    project = factory.SubFactory(OnePercentProjectFactory)
    order = factory.SubFactory(OrderFactory)
    status = 'pending'
