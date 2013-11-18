from django.conf import settings
from django.db import models
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from sorl.thumbnail import ImageField

from apps.fund.models import DonationStatuses


class FundRaiser(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("initiator"), help_text=_("Project owner"))
    project = models.ForeignKey('projects.Project', verbose_name=_("project"))

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    image = ImageField(_("picture"), max_length=255, blank=True, null=True, upload_to='fundraiser_images/', help_text=_("Minimal of 800px wide"))
    video_url = models.URLField(max_length=100, blank=True, default='')

    amount = models.PositiveIntegerField(_("amount (in cents)"))
    currency = models.CharField(max_length="10", default='EUR')
    deadline = models.DateTimeField(null=True)

    created = CreationDateTimeField(_("created"), help_text=_("When this fundraiser was created."))
    updated = ModificationDateTimeField(_('updated'))

    def __unicode__(self):
        return self.title

    @property
    def amount_donated(self):
        # TODO: unittest
        valid_statuses = (DonationStatuses.pending, DonationStatuses.paid)
        donations = self.donation_set.filter(status__in=valid_statuses)
        total = donations.aggregate(sum=Sum('amount'))
        return total['sum'] or '000' # FIXME special formatting due to the way EuroField works