from datetime import timedelta
from bluebottle.bb_projects.models import ProjectTheme, ProjectPhase
from bluebottle.utils.models import Language
from django.utils import timezone
from bluebottle.test.factory_models.projects import ProjectFactory

from apps.projects.models import Project


class OnePercentProjectFactory(ProjectFactory):

    FACTORY_FOR = Project
    deadline = timezone.now() + timedelta(days=30)

    # FIXME: Make sure project related objects are inited before this.
    theme = ProjectTheme.objects.all()[0]
    status = ProjectPhase.objects.get(slug='campaign')
    language = Language.objects.all()[0]
