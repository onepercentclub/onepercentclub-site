from django.core.cache import cache
from django.db import models
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField


class Statistic(models.Model):
    """
    Stats for homepage
    """

    lives_changed = models.IntegerField()
    projects = models.IntegerField()
    countries = models.IntegerField()
    hours_spent = models.IntegerField()
    creation_date = CreationDateTimeField(_('creation date'))

    @property
    def donated(self):
        from apps.fund.models import Donation, DonationStatuses

        """ Add all donation amounts for all donations ever """
        if cache.get('donations-grant-total'):
            return cache.get('donations-grant-total')
        donations = Donation.objects.filter(status__in=(DonationStatuses.pending, DonationStatuses.paid))
        donated = donations.aggregate(sum=Sum('amount'))['sum'] or '000'
        cache.set('donations-grant-total', donated, 300)
        return donated

    def __unicode__(self):
        return 'Site Statistics ' + str(self.creation_date)

