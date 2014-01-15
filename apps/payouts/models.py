import csv
import decimal

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from apps.projects.models import Project
from apps.sepa.sepa import SepaDocument, SepaAccount

from .fields import MoneyField
from .utils import money_from_cents, round_money, get_fee_percentage
from .choices import PayoutLineStatuses, PayoutRules


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
            self.save()

        assert not self.invoice_reference, 'Invoice reference already set!'

        self.invoice_reference = self.generate_invoice_reference()

        if save:
            self.save()


class Payout(InvoiceReferenceBase, models.Model):
    """
    A projects is payed after it's fully funded in the first batch (2x/month).
    Project payouts are checked manually. Selected projects can be exported to a SEPA file.
    """

    planned = models.DateField(_("Planned"), help_text=_("Date that this batch should be processed."))

    project = models.ForeignKey('projects.Project')

    payout_rule = models.CharField(
        _("Payout rule"), max_length=20,
        choices=PayoutRules.choices,
        help_text=_("The payout rule for this project.")
    )

    status = models.CharField(
        _("status"), max_length=20, choices=PayoutLineStatuses.choices)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

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

    def calculate_amounts(self):
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

        # Campaign shorthand
        campaign = self.project.projectcampaign

        if campaign.money_donated >= campaign.money_asked:
            # Fully funded, set payout rule to 5
            self.payout_rule = PayoutRules.five
        else:
            self.payout_rule = PayoutRules.twelve

        fee_factor = get_fee_percentage(self.payout_rule)

        self.amount_raised = money_from_cents(
            campaign.money_donated
        )

        self.organization_fee = self.amount_raised * fee_factor
        self.amount_payable = self.amount_raised - self.organization_fee

        self.save()

    def generate_invoice_reference(self):
        """ Generate invoice reference from project and payout id's. """
        assert self.id
        assert self.project
        assert self.project.id

        return u'%d-%d' % (self.project.id, self.id)

    @property
    def safe_amount_payable(self):
        """ Realtime amount of safe donations received. """
        # Get amount as Decimal
        safe_amount = money_from_cents(self.project.projectcampaign.money_safe)

        # Calculate fee factor
        fee_factor = decimal.Decimal('1.00') - get_fee_percentage(self.payout_rule)

        # Round it
        safe_amount = round_money(safe_amount * fee_factor)

        return safe_amount

    @property
    def is_valid(self):
        """ Whether or not payment details are complete. """
        # TODO: Do a more advanced check. Maybe use IBAN check by a B. Q. Konrath?
        if self.receiver_account_iban and self.receiver_account_bic:
            return True
        return False

    def __unicode__(self):
        date = self.created.strftime('%d-%m-%Y')
        return  self.invoice_reference + " : " + date + " : " + self.receiver_account_number + " : EUR " + str(self.amount_payable)


class OrganizationPayout(models.Model):
    """
    Payouts for organization fees minus costs to the organization spanning
    a particular span of time.

    Organization fees are calculated from completed Payouts to projects and
    are originally including VAT.

    PSP costs are calculated from orders and are originally excluding VAT.

    Other costs (i.e. international banking fees) can be manually specified
    either excluding or including VAT.
    """

    status = models.CharField(
        _("status"), max_length=20, choices=PayoutLineStatuses.choices)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    invoice_reference = models.CharField(max_length=100)

    def calculate_amounts(self):
        """
        Calculate amounts.

        Updates:
         ...

        Should only be called for Payouts with status 'new'.
        """
        assert self.status == PayoutLineStatuses.new, \
            'Can only recalculate for new Payout.'


        # TODO

        self.save()

    def __unicode__(self):
        return u'%(invoice_reference)s from %(start_date)s to %(end_date)s' % {
            'invoice_reference': self.invoice_reference,
            'start_date': self.start_date,
            'end_date': self.end_date
        }


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

post_save.connect(
    create_payout_for_fully_funded_project, weak=False, sender=Project
)
