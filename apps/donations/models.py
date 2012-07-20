from decimal import Decimal

from django.db import models
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
        All legacy values for DonationStatusus.

        TODO: Currently these are related to the payments. This should change
        to information required by the actual use cases
        (ie. payout operations, project and member notifications).
        """
        closed = ChoiceItem('closed', label=_('Closed'))
        expired = ChoiceItem('expired', label=_('Expired'))
        paid = ChoiceItem('paid', label=_('Paid'))
        canceled = ChoiceItem('canceled', label=_('Canceled'))
        chargedback = ChoiceItem('chargedback', label=_('Chargedback'))
        new = ChoiceItem('new', label=_('New'))
        started = ChoiceItem('started', label=_('Started'))

    user = models.ForeignKey('auth.User')
    amount = MoneyField(_('amount'))

    status = models.CharField(_('status'),
        max_length=20, choices=DonationStatuses.choices, db_index=True
    )

    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))

    class Meta:
        verbose_name = _('donation')
        verbose_name_plural = _('donations')

    def __unicode__(self):
        if self.amount:
            try:
                return u'%f on %s from %s' % (
                    self.amount, self.created, self.user
                )
            except ObjectDoesNotExist:
                return u'%f on %s' % (
                    self.amount, self.created
                )

        return str(self.pk)


class DonationLine(models.Model):
    """
    DonationLine, allocating part of a Donation to a specific Project.
    """

    donation = models.ForeignKey(Donation)

    project = models.ForeignKey('projects.Project')
    amount = MoneyField(_('amount'))

    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))

    class Meta:
        verbose_name = _('donation line')
        verbose_name_plural = _('donation lines')

    def __unicode__(self):
        if self.amount:
            try:
                return u'%f from donation %s to %s' % (
                    self.amount, self.donation, self.project
                )
            except ObjectDoesNotExist:
                return u'%f' % self.amount

        return str(self.pk)

    def clean(self):
        """
        Validate that the total DonationLine amount is never more than the
        Donation amount.
        """

        total_amount = self.__class__.objects.filter(
            project=self.project, donation__user=self.donation.user
        ).aggregate(models.Sum('amount'))['amount__sum']

        if not total_amount:
            total_amount = Decimal('0.00')

        total_amount += self.amount

        if total_amount > self.donation.amount:
            raise ValidationError(
                'Requested amount not available.'
            )