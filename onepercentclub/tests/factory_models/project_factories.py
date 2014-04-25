import datetime
from bluebottle.bb_projects.models import ProjectPhase
from bluebottle.test.factory_models.utils import LanguageFactory
import factory

from django.utils.timezone import now

from bluebottle.test.factory_models.projects import (
    ProjectFactory, ProjectPhaseFactory, ProjectThemeFactory)

from apps.projects.models import Project


class OnePercentProjectFactory(ProjectFactory):

    FACTORY_FOR = Project

    def __init__(self):
        super(OnePercentProjectFactory, self).__init__()
        self.init_related_models()


    @classmethod
    def init_related_models(self):
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

        for phase in phase_data:
            ProjectPhaseFactory.create(**phase)

        for theme in theme_data:
            ProjectThemeFactory.create(**theme)

        for language in language_data:
            LanguageFactory.create(**language)
