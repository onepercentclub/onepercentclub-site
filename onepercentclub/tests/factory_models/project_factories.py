import datetime
from bluebottle.test.factory_models.utils import LanguageFactory
import factory

from django.utils.timezone import now

from bluebottle.test.factory_models.projects import (
    ProjectFactory, ProjectPhaseFactory, ProjectThemeFactory)

from apps.projects.models import Project


class OnePercentProjectFactory(ProjectFactory):
    FACTORY_FOR = Project


class OnePercentProjectTestInit():
    """
    Set up some basic models needed for project creation.
    """

    phases = [{'name' :'Plan - New'},
              {'name': 'Plan - Submitted'},
              {'name': 'Plan - Rejected'},
              {'name': 'Campaign'},
              {'name': 'Stopped'},
              {'name': 'Done - Complete'},
              {'name': 'Done - Incomplete'}]

    themes = [{'name': 'Education'},
              {'name': 'Environment'}]

    languages = [{'code': 'en', 'language_name': 'English', 'native_name': 'English'},
                 {'code': 'nl', 'language_name': 'Dutch', 'native_name': 'Nederlands'}]

    def __init__(self):

        for phase in self.phases:
            ProjectPhaseFactory.create(**phase)

        for theme in self.themes:
            ProjectThemeFactory.create(**theme)

        for language in self.languages:
            LanguageFactory.create(**language)
