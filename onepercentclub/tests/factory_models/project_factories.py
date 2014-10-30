import datetime
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now

from bluebottle.test.factory_models.projects import ProjectFactory
from apps.projects.models import Project, PartnerOrganization
import factory

class OnePercentProjectFactory(ProjectFactory):
    FACTORY_FOR = Project

    deadline = timezone.now() + timedelta(days=30)
    amount_needed = 100
    amount_asked = 100
    allow_overfunding = True


class PartnerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PartnerOrganization

    FACTORY_DJANGO_GET_OR_CREATE = ('slug',)

    name = factory.Sequence(lambda n: 'Partner_{0}'.format(n))
    slug = factory.Sequence(lambda n: 'partner-{0}'.format(n))
    description = 'Partner Organization factory model'

