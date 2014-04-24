import csv
import decimal

import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from apps.sepa.sepa import SepaDocument, SepaAccount
from apps.cowry.models import Payment, PaymentStatuses

from .fields import MoneyField
from .utils import (
    money_from_cents, round_money,
    calculate_vat, calculate_vat_exclusive, date_timezone_aware
)
from .choices import PayoutLineStatuses, PayoutRules

from bluebottle.utils.utils import get_project_model

#PROJECT_MODEL = get_project_model()


class InvoiceReferenceBase(models.Model):
    """ Abstract base class for generating an invoice reference. """

    invoice_reference = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def generate_invoice_reference(self):
        """ Generate invoice reference. """

        assert self.id, 'Object should be saved first.'

        return unicode(self.id)

    def update_invoice_reference(self, auto_save=False, save=True):
        """
        Generate and save (when save=True) invoice reference.
        Automatically saves to generate an id when auto_save is set.
        """

        if auto_save and not self.id:
            # Save to generate self.id
            super(InvoiceReferenceBase, self).save()

        assert not self.invoice_reference, 'Invoice reference already set!'

        self.invoice_reference = self.generate_invoice_reference()

        if save:
            super(InvoiceReferenceBase, self).save()


class CompletedDateTimeBase(models.Model):
    """
    Abstract base class for Payout objects logging when the status is changed
    from progress to completed in a 'completed' field.
    """

    # The timestamp the order changed to completed. This is auto-set in the save() method.
    completed = models.DateField(
        _("Closed"), blank=True, null=True, help_text=_(
            'Book date when the bank transaction was confirmed and '
            'the payout has been set to completed.'
        )
    )

    class Meta:
        abstract = True

    def clean(self):
        """ Validate completed/completed date consistency. """

        if self.completed and self.status != PayoutLineStatuses.completed:
            raise ValidationError(
                _('Closed date is set but status is not completed.')
            )

    def save(self, *args, **kwargs):
        if self.status == PayoutLineStatuses.completed and not self.completed:
            # No completed date was set and our current status is completed
            self.completed = timezone.now()

        super(CompletedDateTimeBase, self).save(*args, **kwargs)


class PayoutBase(InvoiceReferenceBase, CompletedDateTimeBase, models.Model):
    """
    Common abstract base class for Payout and OrganizationPayout.
    """
    planned = models.DateField(_("Planned"),
        help_text=_("Date on which this batch should be processed.")
    )

    status = models.CharField(
        _("status"), max_length=20, choices=PayoutLineStatuses.choices,
        default=PayoutLineStatuses.new
    )
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    class Meta:
        abstract = True

    def _get_old_status(self):
        """ Get previous status based on state change logs. """

        assert self.pk

        try:
            latest_state_change = self.log_set.latest()
            return latest_state_change.new_status

        except ObjectDoesNotExist:
            # First state change, no previous state
            return None

    def _log_status_change(self):
        """ Log the change from one status to another. """

        old_status = self._get_old_status()

        if old_status != self.status:
            # Create log entry
            log_entry = self.log_set.model(
                payout=self,
                old_status=old_status, new_status=self.status
            )
            log_entry.save()

            return log_entry

    def save(self, *args, **kwargs):
        """
        Make sure we log a state change after saving.
        """

        result = super(PayoutBase, self).save(*args, **kwargs)

        self._log_status_change()

        return result


class PayoutLogBase(models.Model):
    """
    Abstract base class for logging state changes.

    Requires a 'payout' ForeignKey with related_name='log_set' to be defined.
    """

    class Meta:
        verbose_name = _('state change')
        verbose_name_plural = _('state changes')
        abstract = True

        ordering = ['-date']
        get_latest_by = 'date'

    date = CreationDateTimeField(_("date"))

    old_status = models.CharField(
        _("old status"), max_length=20, choices=PayoutLineStatuses.choices,
        blank=True, null=True
    )

    new_status = models.CharField(
        _("new status"), max_length=20, choices=PayoutLineStatuses.choices,
    )

    def __unicode__(self):
        return _(
            u'Status change of \'%(payout)s\' on %(date)s from %(old_status)s to %(new_status)s' % {
                'payout': unicode(self.payout),
                'date': self.date.strftime('%d-%m-%Y'),
                'old_status': self.old_status,
                'new_status': self.new_status,
            }
        )


class Payout(PayoutBase):
    """
    A projects is payed after it's fully funded in the first batch (2x/month).
    Project payouts are checked manually. Selected projects can be exported to a SEPA file.
    """

    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL)

    payout_rule = models.CharField(
        _("Payout rule"), max_length=20,
        choices=PayoutRules.choices,
        help_text=_("The payout rule for this project.")
    )

    amount_raised = MoneyField(
        _("amount raised"),
        help_text=_('Amount raised when Payout was created or last recalculated.')
    )

    organization_fee = MoneyField(
        _("organization fee"),
        help_text=_('Fee substracted from amount raised for the organization.')
    )

    amount_payable = MoneyField(
        _("amount payable"),
        help_text=_('Payable amount; raised amount minus organization fee.')
    )

    sender_account_number = models.CharField(max_length=100)
    receiver_account_number = models.CharField(max_length=100, blank=True)
    receiver_account_iban = models.CharField(max_length=100, blank=True)
    receiver_account_bic = models.CharField(max_length=100, blank=True)
    receiver_account_name = models.CharField(max_length=100)
    receiver_account_city = models.CharField(max_length=100)
    receiver_account_country = models.CharField(max_length=100, null=True)

    description_line1 = models.CharField(max_length=100, blank=True, default="")
    description_line2 = models.CharField(max_length=100, blank=True, default="")
    description_line3 = models.CharField(max_length=100, blank=True, default="")
    description_line4 = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']

    def _get_fee_percentage(self):
        """
        Get fee percentag according to the current PayoutRule.

        Note: this should *only* be called internally.
        """
        assert self.payout_rule

        if self.payout_rule == PayoutRules.five:
            # 5%
            return decimal.Decimal('0.05')

        elif self.payout_rule == PayoutRules.seven:
            # 7%
            return decimal.Decimal('0.07')

        elif self.payout_rule == PayoutRules.twelve:
            # 12%
            return decimal.Decimal('0.12')

        # Other
        raise NotImplementedError('Payment rule not implemented yet.')

    def _get_payout_rule(self):
        """
        Return the payout rule considering the current state of the Payout.

        Note: this should *only* be called internally.
        """
        assert self.project
        assert self.project.projectcampaign

        # Campaign shorthand
        campaign = self.project.projectcampaign

        # 1st of January 2014
        start_2014 = date_timezone_aware(datetime.date(2014, 1, 1))

        if campaign.created >= start_2014:
            # New rules per 2014

            if campaign.money_donated >= campaign.money_asked:
                # Fully funded

                # New default payout rule is 7 percent
                return PayoutRules.seven

            else:
                # Not fully funded
                return PayoutRules.twelve

        # Campaign started before 2014
        # Always 5 percent
        return PayoutRules.five

    def calculate_amounts(self, save=True):
        """
        Calculate amounts according to payment_rule.

        Updates:
          - payout_rule
          - amount_raised
          - organization_fee
          - amount_payable

        Should only be called for Payouts with status 'new'.
        """
        assert self.status == PayoutLineStatuses.new, \
            'Can only recalculate for new Payout.'

        self.payout_rule = self._get_payout_rule()
        fee_factor = self._get_fee_percentage()

        self.amount_raised = self.get_amount_raised()

        self.organization_fee = self.amount_raised * fee_factor
        self.amount_payable = self.amount_raised - self.organization_fee

        if save:
            self.save()

    def generate_invoice_reference(self):
        """ Generate invoice reference from project and payout id's. """
        assert self.id
        assert self.project
        assert self.project.id

        return u'%d-%d' % (self.project.id, self.id)

    def get_amount_raised(self):
        """ Realtime amount of raised ('paid', 'pending') donations. """

        # Get amount as Decimal
        amount = round_money(
            money_from_cents(self.project.amount_donated)
        )

        return amount

    def get_amount_safe(self):
        #TODO: what is this?
        """ Realtime amount of safe ('paid') donations. """
        # Get amount as Decimal
        amount = round_money(
            money_from_cents(self.project.projectcampaign.money_safe)
        )

        return amount

    def get_amount_pending(self):
        """ Realtime amount of pending donations. """
        # Get amount as Decimal
        amount = round_money(
            money_from_cents(self.project.projectcampaign.money_pending)
        )

        return amount

    def get_amount_failed(self):
        """
        Realtime difference between saved amount_raised, safe and pending.

        Note: amount_raised is the saved property, other values are realtime.
        """

        amount_safe = self.get_amount_safe()
        amount_pending = self.get_amount_pending()

        amount_failed = self.amount_raised - amount_safe - amount_pending

        if amount_failed <= decimal.Decimal('0.00'):
            # Should never be less than 0
            return decimal.Decimal('0.00')

        return amount_failed

    def __unicode__(self):
        date = self.created.strftime('%d-%m-%Y')
        return  self.invoice_reference + " : " + date + " : " + self.receiver_account_number + " : EUR " + str(self.amount_payable)


class PayoutLog(PayoutLogBase):
    payout = models.ForeignKey(Payout, related_name='log_set')


class OrganizationPayout(PayoutBase):
    """
    Payouts for organization fees minus costs to the organization spanning
    a particular span of time.

    Organization fees are calculated from completed Payouts to projects and
    are originally including VAT.

    PSP costs are calculated from orders and are originally excluding VAT.

    Other costs (i.e. international banking fees) can be manually specified
    either excluding or including VAT.

    Note: Start and end dates are inclusive.
    """
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    organization_fee_excl = MoneyField(_('organization fee excluding VAT'))
    organization_fee_vat = MoneyField(_('organization fee VAT'))
    organization_fee_incl = MoneyField(_('organization fee including VAT'))

    psp_fee_excl = MoneyField(_('PSP fee excluding VAT'))
    psp_fee_vat = MoneyField(_('PSP fee VAT'))
    psp_fee_incl = MoneyField(_('PSP fee including VAT'))

    other_costs_excl = MoneyField(
        _('other costs excluding VAT'), default=decimal.Decimal('0.00'),
        help_text=_(
            'Set either this value or inclusive VAT, make sure recalculate afterwards.'
        )
    )
    other_costs_vat = MoneyField(
        _('other costs VAT'), default=decimal.Decimal('0.00'))
    other_costs_incl = MoneyField(
        _('other costs including VAT'), default=decimal.Decimal('0.00'),
        help_text=_(
            'Set either this value or exclusive VAT, make sure recalculate afterwards.'
        )
    )

    payable_amount_excl = MoneyField(_('payable amount excluding VAT'))
    payable_amount_vat = MoneyField(_('payable amount VAT'))
    payable_amount_incl = MoneyField(_('payable amount including VAT'))

    class Meta:
        unique_together = ('start_date', 'end_date')
        get_latest_by = 'end_date'
        ordering = ['start_date']

    def _get_organization_fee(self):
        """
        Calculate and return the organization fee for Payouts within this
        OrganizationPayout's period, including VAT.

        Note: this should *only* be called internally.
        """
        # Get Payouts
        payouts = Payout.objects.filter(
            completed__gte=self.start_date,
            completed__lte=self.end_date
        )

        # Aggregate value
        aggregate = payouts.aggregate(models.Sum('organization_fee'))

        # Return aggregated value or 0.00
        fee = aggregate.get(
            'organization_fee__sum', decimal.Decimal('0.00')
        ) or decimal.Decimal('0.00')

        return fee

    def _get_psp_fee(self):
        """
        Calculate and return Payment Service Provider fee from
        payments relating through orders to donations which became irrevocably
        paid during the OrganizationPayout period, excluding VAT.

        Note: this should *only* be called internally.
        """
        # Allowed payment statusus (statusus generating fees)
        # In apps.cowry_docdata.adapters it appears that fees are only
        # calculated for the paid status, with implementation for chargedback
        # coming. There are probably other fees
        allowed_statuses = (
            PaymentStatuses.paid,
            PaymentStatuses.chargedback,
            PaymentStatuses.refunded
        )

        payments = Payment.objects.filter(
            status__in=allowed_statuses
        )

        # Do a silly trick by filtering the date the donation became paid
        # (the only place where the Docdata closed/paid status is matched).
        payments = payments.order_by('order__donations__ready')
        payments = payments.filter(
            order__donations__ready__gte=date_timezone_aware(self.start_date),
            order__donations__ready__lte=date_timezone_aware(self.end_date)
        )

        # Make sure this does not create additional objects
        payments = payments.distinct()

        # Aggregate the variable fees and count the amount of payments
        aggregate = payments.aggregate(models.Sum('fee'))

        # Aggregated value (in cents) or 0
        fee = aggregate.get('fee__sum', 0) or 0

        return money_from_cents(fee)

    def calculate_amounts(self, save=True):
        """
        Calculate amounts. If save=True, saves the result.

        Should only be called for Payouts with status 'new'.
        """
        assert self.status == PayoutLineStatuses.new, \
            'Can only recalculate for new Payout.'

        # Calculate original values
        self.organization_fee_incl = self._get_organization_fee()
        self.psp_fee_excl = self._get_psp_fee()

        assert isinstance(self.organization_fee_incl, decimal.Decimal)
        assert isinstance(self.psp_fee_excl, decimal.Decimal)

        # VAT calculations
        self.organization_fee_excl = calculate_vat_exclusive(self.organization_fee_incl)
        self.organization_fee_vat = self.organization_fee_incl - self.organization_fee_excl

        self.psp_fee_vat = calculate_vat(self.psp_fee_excl)
        self.psp_fee_incl = self.psp_fee_excl + self.psp_fee_vat

        # Conditionally calculate VAT for other_costs
        if self.other_costs_incl and not self.other_costs_excl:
            # Inclusive VAT set, calculate exclusive
            self.other_costs_excl = calculate_vat_exclusive(self.other_costs_incl)
            self.other_costs_vat = self.other_costs_incl - self.other_costs_excl

        elif self.other_costs_excl and not self.other_costs_incl:
            # Exclusive VAT set, calculate inclusive
            self.other_costs_vat = calculate_vat(self.other_costs_excl)
            self.other_costs_incl = self.other_costs_excl + self.other_costs_vat

        # Calculate payable amount
        self.payable_amount_excl =  (
            self.organization_fee_excl - self.psp_fee_excl - self.other_costs_excl
        )
        self.payable_amount_vat =  (
            self.organization_fee_vat - self.psp_fee_vat - self.other_costs_vat
        )
        self.payable_amount_incl = (
            self.organization_fee_incl - self.psp_fee_incl - self.other_costs_incl
        )

        if save:
            self.save()

    def clean(self):
        """ Validate date span consistency. """

        # End date should lie after start_date
        if self.start_date >= self.end_date:
            raise ValidationError(_('Start date should be earlier than date.'))

        if not self.id:
            # Validation for new objects

            # There should be no holes in periods between payouts
            try:
                latest = self.__class__.objects.latest()
                next_date = latest.end_date + datetime.timedelta(days=1)

                if next_date != self.start_date:
                    raise ValidationError(_('The next payout period should start the day after the end of the previous period.'))

            except self.__class__.DoesNotExist:
                # No earlier payouts exist
                pass

        else:
            # Validation for existing objects

            # Check for consistency before changing into 'progress'.
            old_status = self.__class__.objects.get(id=self.id).status

            if (
                old_status == PayoutLineStatuses.new and
                self.status == PayoutLineStatuses.progress
            ):
                # Old status: new
                # New status: progress

                # Check consistency of other costs
                if (
                    self.other_costs_incl - self.other_costs_excl != self.other_costs_vat
                ):
                    raise ValidationError(_('Other costs have changed, please recalculate before progessing.'))

        # TODO: Prevent overlaps

        super(OrganizationPayout, self).clean()

    def save(self, *args, **kwargs):
        """
        Calculate values on first creation and generate invoice reference.
        """

        if not self.id:
            # No id? Not previously saved

            if self.status == PayoutLineStatuses.new:
                # This exists mainly for testing reasons, payouts should
                # always be created new
                self.calculate_amounts(save=False)

            if not self.invoice_reference:
                # Conditionally creat invoice reference
                self.update_invoice_reference(auto_save=True, save=False)

        super(OrganizationPayout, self).save(*args, **kwargs)

    def generate_invoice_reference(self):
        """ Generate invoice reference from project and payout id's. """
        assert self.id

        return u'%(year)d-OP%(payout_id)04d' % {
            'year': self.created.year,
            'payout_id': self.id
        }

    def __unicode__(self):
        return u'%(invoice_reference)s from %(start_date)s to %(end_date)s' % {
            'invoice_reference': self.invoice_reference,
            'start_date': self.start_date,
            'end_date': self.end_date
        }


class OrganizationPayoutLog(PayoutLogBase):
    payout = models.ForeignKey(OrganizationPayout, related_name='log_set')


class BankMutationLine(models.Model):

    created = CreationDateTimeField(_("Created"))
    bank_mutation = models.ForeignKey("payouts.BankMutation")

    issuer_account_number = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    start_date = models.DateField(_("Date started"))
    dc = models.CharField(_("Debet/Credit"), max_length=1)
    amount = models.DecimalField(decimal_places=2, max_digits=15)
    account_number = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=10)

    invoice_reference = models.CharField(max_length=100)

    description_line1 = models.CharField(max_length=100, blank=True, default="")
    description_line2 = models.CharField(max_length=100, blank=True, default="")
    description_line3 = models.CharField(max_length=100, blank=True, default="")
    description_line4 = models.CharField(max_length=100, blank=True, default="")

    payout = models.ForeignKey("payouts.Payout", null=True)

    def __unicode__(self):
        return str(self.start_date) + " " + self.dc + " : " + self.account_name + " [" + self.account_number + "]  " + \
            " EUR " + str(self.amount)


class BankMutation(models.Model):

    created = CreationDateTimeField(_("Created"))
    mut_file = models.FileField(_("Uploaded mutation file"), upload_to="bank_mutations", null=True)
    mutations = models.TextField(blank=True)

    def save(self, force_insert=False, force_update=False, using=None):
        super(BankMutation, self).save()
        self.mutations = self.mut_file.read()
        self.parse_file()
        self.mut_file = None

    def parse_file(self):
        mutations = csv.reader(self.mut_file)
        for m in mutations:
            if len(m) > 1:
                date = m[2]
                date = date[0:4] + "-" + date[4:6] + "-" + date[6:]
                line = BankMutationLine(issuer_account_number=m[0], currency=m[1], start_date=date, dc=m[3],
                                        amount=m[4], account_number=m[5], account_name=m[6], transaction_type=m[8],
                                        invoice_reference=m[10], description_line1=m[11], description_line2=m[12],
                                        description_line3=m[13], description_line4=m[14],
                                        bank_mutation=self)
                line.save()
        match_debit_mutations()

    def __unicode__(self):
        return "Bank Mutations " + str(self.created.strftime('%B %Y'))


# TODO: These should probably be methods of some model somewhere
def create_sepa_xml(payouts):
    batch_id = timezone.datetime.strftime(timezone.now(), '%Y%m%d%H%I%S')
    sepa = SepaDocument(type='CT')
    debtor = SepaAccount(name=settings.SEPA['name'], iban=settings.SEPA['iban'], bic=settings.SEPA['bic'])
    sepa.set_debtor(debtor)
    sepa.set_info(message_identification=batch_id, payment_info_id=batch_id)
    sepa.set_initiating_party(name=settings.SEPA['name'], id=settings.SEPA['id'])

    for line in payouts.all():
        creditor = SepaAccount(name=line.receiver_account_name, iban=line.receiver_account_iban,
                               bic=line.receiver_account_bic)
        sepa.add_credit_transfer(creditor=creditor, amount=line.amount, creditor_payment_id=line.invoice_reference)
    return sepa.as_xml()


def match_debit_mutations():
    lines = BankMutationLine.objects.filter(dc='D', payout__isnull=True).all()
    for line in lines:

        date = line.start_date

        try:
            payout = Payout.objects.filter(invoice_reference=line.invoice_reference).get()
            line.matched = True
            line.payout_line = payout
            line.save()
            payout.status = Payout.PayoutLineStatuses.completed
            payout.save()

            payout.project.payout_date = date
            payout.project.save()

        except Payout.DoesNotExist:
            pass


# Connect signals after defining models
# Ref:  http://stackoverflow.com/a/9851875
# Note: for newer Django, put this in module initialization code
# https://docs.djangoproject.com/en/dev/topics/signals/#django.dispatch.receiver
from .signals import create_payout_for_fully_funded_project

# post_save.connect(
#     create_payout_for_fully_funded_project, weak=False, sender=PROJECT_MODEL
# )
