from bluebottle.bb_projects.models import ProjectPhase
from bluebottle.geo.models import Country
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.geo import CountryFactory
from django.core.urlresolvers import reverse
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.utils import OnePercentTestCase
from rest_framework import status


class MonthlyDonationCommandsTest(OnePercentTestCase):

    def setUp(self):
        self.init_projects()
        self.phase_campaign = ProjectPhase.objects.get(slug='campaign')
        self.country = CountryFactory()

        self.projects = []

        for amount in [500, 100, 1500, 300, 200]:
            self.projects.append(OnePercentProjectFactory.create(amount_asked=amount, status=self.phase_campaign))

        self.some_user = BlueBottleUserFactory.create()
        self.another_user = BlueBottleUserFactory.create()

    def test_top_3(self):
        pass

    def test_preselected(self):
        pass

    def test_recent_recurring_donation(self):
        pass

    def test_more_stuff(self):
        pass
