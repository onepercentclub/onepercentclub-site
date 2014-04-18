import datetime
import factory

from django.utils.timezone import now

from bluebottle.test.factory_models.projects import (
    ProjectFactory, ProjectPhaseFactory, ProjectThemeFactory)

from apps.projects.models import Project


class OnePercentProjectFactory(ProjectFactory):
    FACTORY_FOR = Project