from django.conf import settings
from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from django.utils.translation import ugettext as _


class MonthlyDonationBatch(models.Model):

    date = models.DateField()
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))

class MonthlyDonation(models.Model):

    batch = models.ForeignKey(MonthlyDonationBatch)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.PositiveIntegerField(_("amount in cents"), default=0)
    currency = models.CharField(max_length=3, default='EUR')
    name = models.CharField(max_length=35)
    city = models.CharField(max_length=35)
    iban = IBANField(blank=True, default='')
    bic = SWIFTBICField(blank=True, default='')


class MonthlyDonationProject(models.Model):

    donation = models.ForeignKey(MonthlyDonation)
    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL)
    amount = models.PositiveIntegerField(_("amount in cents"), default=0)

