from apps.fund.models import Donation
from django.db.models.aggregates import Sum
from django.utils.timezone import now
from django.core.cache import cache

from apps.banners.models import Slide
from apps.campaigns.models import Campaign
from apps.fundraisers.models import FundRaiser
from apps.projects.models import Project
from apps.quotes.models import Quote
from apps.statistics.models import Statistic


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
        projects = Project.objects.filter(phase='campaign').order_by('?')
        if len(projects) > 4:
            self.projects = projects[0:4]
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

        self.donated = self.sum_donations

        return self

    @property
    def sum_donations(self):

        """ Add all donation amounts for all donations ever """
        if cache.get('donations-grant-total'):
            return cache.get('donations-grant-total')

        donations = Donation.valid_donations
        donated = donations.aggregate(sum=Sum('amount'))['sum'] or '000'
        cache.set('donations-grant-total', donated, 300)
        return donated

