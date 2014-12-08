from bluebottle.bb_projects.models import ProjectPhase
from django.utils.timezone import now

from bluebottle.slides.models import Slide
from bluebottle.quotes.models import Quote

from apps.campaigns.models import Campaign
from bluebottle.fundraisers.models import FundRaiser
from apps.statistics.models import Statistic

from bluebottle.utils.model_dispatcher import get_project_model

PROJECT_MODEL = get_project_model()

# Instead of serving all the objects separately we combine Slide, Quote and Stats into a dummy object

class HomePage(object):

    def get(self, language):
        self.id = 1
        self.quotes= Quote.objects.published().filter(language=language)
        self.slides = Slide.objects.published().filter(language=language)
        stats = Statistic.objects.order_by('-creation_date').all()
        if len(stats) > 0:
            self.stats = stats[0]
        else:
            self.stats = None
        if language == 'en':
            projects = PROJECT_MODEL.objects.filter(is_campaign=True).filter(language__code=language).order_by('?')
        else:
            projects = PROJECT_MODEL.objects.filter(is_campaign=True).order_by('?')

        if len(projects) > 3:
            self.projects = projects[0:3]
        elif len(projects) > 0:
            self.projects = projects[0:len(projects)]
        else:
            self.projects = None

        try:
            self.campaign = Campaign.objects.get(start__lte=now(), end__gte=now())
            # NOTE: MultipleObjectsReturned is not caught yet!
            self.fundraisers = FundRaiser.objects.filter(project__is_campaign=True).order_by('-created')
        except Campaign.DoesNotExist:
            self.campaign, self.fundraisers = None, None

        return self


