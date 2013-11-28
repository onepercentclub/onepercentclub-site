from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from apps.fund.models import Donation


class Campaign(models.Model):
    title = models.CharField(_('title'), max_length=255)
    start = models.DateTimeField(_('start'))
    end = models.DateTimeField(_('end'))

    target = models.PositiveIntegerField(_("target (in cents)"))
    currency = models.CharField(max_length="10", default='EUR')

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)

    class Meta:
        verbose_name = _(u'campaign')
        verbose_name_plural = _(u'campaigns')
        ordering = ['-start']

    def __unicode__(self):
        return self.title

    @property
    def sum_donations(self):
        """ Add all donation amounts for donations made between start and end of the campaign """
        donations = Donation.valid_donations.filter(ready__gte=self.start).filter(ready__lte=self.end)
        donated = donations.aggregate(sum=Sum('amount'))['sum']
        return donated or '000'

