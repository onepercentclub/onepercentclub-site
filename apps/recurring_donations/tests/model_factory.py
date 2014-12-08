import factory
from apps.recurring_donations.models import MonthlyDonor, MonthlyDonorProject
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.geo import CountryFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory


class MonthlyDonorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MonthlyDonor

    user = factory.SubFactory(BlueBottleUserFactory)

    active = True
    amount = 25
    iban = 'NL13TEST0123456789'
    bic = 'TESTNL2A'
    name = factory.Sequence(lambda n: 'Some Name {0}'.format(n))
    city = factory.Sequence(lambda n: 'Some City {0}'.format(n))
    country = factory.SubFactory(CountryFactory)


class MonthlyDonorProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MonthlyDonorProject

    project = factory.SubFactory(OnePercentProjectFactory)
    donor = factory.SubFactory(MonthlyDonorFactory)

