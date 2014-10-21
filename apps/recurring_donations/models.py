from django.conf import settings
from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from django.utils.translation import ugettext as _


class MonthlyDonor(models.Model):
    """
    Information about a user that wants to donate monthly.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    active = models.BooleanField(default=False)
    amount = models.DecimalField(_("amount"), max_digits=6, decimal_places=2)

    iban = IBANField(blank=True, default='')
    bic = SWIFTBICField(blank=True, default='')
    name = models.CharField(max_length=35)
    city = models.CharField(max_length=35)
    country = models.ForeignKey('geo.Country', blank=True, null=True)

    @property
    def amount_in_cents(self):
        return int(self.amount*100)

    @property
    def is_valid(self):
        # Check if we're above the DocData minimum for direct debit.
        if self.amount < 1.13:
            return False

        # Check if the IBAN / BIC is stored correctly.
        if self.iban == '' or self.bic == '' or self.bic[:4] != self.iban[4:8]:
            return False

        # Check if the IBAN / BIC is match.
        # FIXME: Check if this goes for all IBAN/Bic or just just for The Netherlands.
        if self.bic[:4] != self.iban[4:8]:
            return False

        return True


class MonthlyDonorProject(models.Model):
    """
    Preferred projects by a monthly donor.
    """

    donor = models.ForeignKey(MonthlyDonor, related_name='projects')
    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL)


class MonthlyBatch(models.Model):

    date = models.DateField()
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))

    def __unicode__(self):
        return "{0} {1}".format(self.id, self.date)

    class Meta:
        verbose_name = _('Monthly batch')
        verbose_name_plural = _('Monthly batches')


class MonthlyProject(models.Model):
    """
    Aggregated amount for projects.
    """

    batch = models.ForeignKey(MonthlyBatch)
    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL)
    amount = models.DecimalField(_("amount"), default=0, max_digits=6, decimal_places=2)


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


