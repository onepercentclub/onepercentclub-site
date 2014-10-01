from django.conf import settings
from django.db import models
from django.db.models.aggregates import Sum
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from django.utils.translation import ugettext as _


class MonthlyBatch(models.Model):

    date = models.DateField()
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))

    def __unicode__(self):
        return "{0} {1}".format(self.id, self.date)


class MonthlyOrder(models.Model):

    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))

    batch = models.ForeignKey(MonthlyBatch)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.PositiveIntegerField(_("amount in cents"), default=0)
    currency = models.CharField(max_length=3, default='EUR')
    name = models.CharField(max_length=35)
    city = models.CharField(max_length=35)
    iban = IBANField(blank=True, default='')
    bic = SWIFTBICField(blank=True, default='')

    def __unicode__(self):
        return "{0}: {1}".format(self.user, self.amount)


class MonthlyDonation(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    order = models.ForeignKey(MonthlyOrder, related_name='donations')
    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL)
    amount = models.PositiveIntegerField(_("amount in cents"), default=0)


