import datetime
from bluebottle.bb_projects.models import ProjectPhase
from bluebottle.test.factory_models.utils import LanguageFactory
import factory

from django.utils.timezone import now

from bluebottle.test.factory_models.projects import (
    ProjectFactory, ProjectPhaseFactory, ProjectThemeFactory)

from apps.projects.models import Project


class OnePercentProjectTestInit():
    """
    Set up some basic models needed for project creation.
    """

    phase_data = [{'id': 1, 'name':'Plan - New'},
              {'id': 2, 'name': 'Plan - Submitted'},
              {'id': 3, 'name': 'Plan - Rejected'},
              {'id': 4, 'name': 'Campaign'},
              {'id': 5, 'name': 'Stopped'},
              {'id': 6, 'name': 'Done - Complete'},
              {'id': 7, 'name': 'Done - Incomplete'}]

    theme_data = [{'id': 1, 'name': 'Education'},
              {'id': 2, 'name': 'Environment'}]

    language_data = [{'id': 1, 'code': 'en', 'language_name': 'English', 'native_name': 'English'},
                 {'id': 2, 'code': 'nl', 'language_name': 'Dutch', 'native_name': 'Nederlands'}]

    def __init__(self):

        for phase in self.phase_data:
            ProjectPhaseFactory.create(**phase)

        for theme in self.theme_data:
            ProjectThemeFactory.create(**theme)

        for language in self.language_data:
            LanguageFactory.create(**language)



class OnePercentProjectFactory(ProjectFactory):

    FACTORY_FOR = Project

    status = ProjectPhaseFactory.create(**OnePercentProjectTestInit.phase_data[0])
    theme = ProjectThemeFactory.create(**OnePercentProjectTestInit.theme_data[0])