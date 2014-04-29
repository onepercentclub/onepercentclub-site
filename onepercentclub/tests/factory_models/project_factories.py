import datetime
from bluebottle.bb_projects.models import ProjectPhase, ProjectTheme
from bluebottle.test.factory_models.utils import LanguageFactory
from bluebottle.utils.models import Language
import factory

from django.utils.timezone import now

from bluebottle.test.factory_models.projects import (
    ProjectFactory, ProjectPhaseFactory, ProjectThemeFactory)

from apps.projects.models import Project


class OnePercentProjectFactory(ProjectFactory):

    FACTORY_FOR = Project

