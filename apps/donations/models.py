from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.db.models.base import ObjectDoesNotExist

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)

from djchoices import DjangoChoices, ChoiceItem

from apps.bluebottle_utils.fields import MoneyField


class Donation(models.Model):
    """
    Donation of an amount from a user to one or multiple projects through
    DonationLine objects.
    """

    class DonationStatuses(DjangoChoices):
        """
        These statuses are based on the legacy models and need to be updated
        when we actually sort out payments / donations properly, modelled
        after the actual use cases (ie. payout operations, project and
        member notifications). (TODO)
        """
        closed = ChoiceItem('closed', label=_("Closed"))
        expired = ChoiceItem('expired', label=_("Expired"))
        paid = ChoiceItem('paid', label=_("Paid"))
        canceled = ChoiceItem('canceled', label=_("Canceled"))
        chargedback = ChoiceItem('chargedback', label=_("Chargedback"))
        new = ChoiceItem('new', label=_("New"))
        started = ChoiceItem('started', label=_("Started"))

    user = models.ForeignKey('auth.User', verbose_name=_("user"))
    amount = MoneyField(_("amount"))

    # Note: having an index here allows for efficient filtering by status.
    status = models.CharField(_("status"),
        max_length=20, choices=DonationStatuses.choices, db_index=True
    )

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        if self.amount:
            try:
                return _(u"%(amount)s on %(date)s from %(user)s") % {
                    'amount': self.amount,
                    'date': self.created,
                    'user': self.user
                }
            except ObjectDoesNotExist:
                return _(u"%(amount)s on %(date)s") % {
                    'amount': self.amount,
                    'date': self.created
                }

        return str(self.pk)


class DonationLine(models.Model):
    """
    DonationLine, allocating part of a Donation to a specific Project.
    """

    donation = models.ForeignKey(Donation, verbose_name=_("donation"))

    project = models.ForeignKey('projects.Project', verbose_name=_("project"))
    amount = MoneyField(_("amount"))

    class Meta:
        verbose_name = _("donation line")
        verbose_name_plural = _("donation lines")

    def __unicode__(self):
        if self.amount:
            try:
                return _(
                    u"%(amount)s from donation %(donation)s "
                    u"to %(project)s"
                ) % {
                    'amount': self.amount,
                    'donation': self.donation,
                    'project': self.project
                }

            except ObjectDoesNotExist:
                return u"%s" % self.amount

        return str(self.pk)

    def clean(self):
        """
        Validate that the total DonationLine amount is never more than the
        Donation amount.
        """

        donationlines = self.donation.donationline_set.exclude(pk=self.pk)
        total_amount = \
            donationlines.aggregate(models.Sum('amount'))['amount__sum']

        if not total_amount:
            total_amount = Decimal('0.00')

        total_amount += self.amount

        if total_amount > self.donation.amount:
            raise ValidationError(
                _("Requested amount not available.")
            )
