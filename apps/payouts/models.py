import csv

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.dispatch import receiver

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from apps.projects.models import Project, ProjectPhases
from apps.sepa.sepa import SepaDocument, SepaAccount

from .fields import MoneyField
from .utils import money_from_cents
from .choices import PayoutLineStatuses, PayoutRules


class Payout(models.Model):
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
        _("amount raised"), help_text=_('Amount raised when Payout was created.')
    )

    sender_account_number = models.CharField(max_length=100)
    receiver_account_number = models.CharField(max_length=100, blank=True)
    receiver_account_iban = models.CharField(max_length=100, blank=True)
    receiver_account_bic = models.CharField(max_length=100, blank=True)
    receiver_account_name = models.CharField(max_length=100)
    receiver_account_city = models.CharField(max_length=100)
    receiver_account_country = models.CharField(max_length=100, null=True)

    invoice_reference = models.CharField(max_length=100)
    description_line1 = models.CharField(max_length=100, blank=True, default="")
    description_line2 = models.CharField(max_length=100, blank=True, default="")
    description_line3 = models.CharField(max_length=100, blank=True, default="")
    description_line4 = models.CharField(max_length=100, blank=True, default="")

    @property
    def amount_payout(self):
        return '%.2f' % (float(self.amount) / 100)

    @property
    def current_amount_safe(self):
        return '%.2f' % (self.project.projectcampaign.money_safe * settings.PROJECT_PAYOUT_RATE / 100)

    @property
    def is_valid(self):
        # TODO: Do a more advanced check. Maybe use IBAN check by a B. Q. Konrath?
        if self.receiver_account_iban and self.receiver_account_bic:
            return True
        return False

    @property
    def amount_safe(self):
        return int(round(self.project.projectcampaign.money_safe * settings.PROJECT_PAYOUT_RATE))

    def __unicode__(self):
        date = self.created.strftime('%d-%m-%Y')
        return  self.invoice_reference + " : " + date + " : " + self.receiver_account_number + " : EUR " + str(self.amount_payout)


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



@receiver(post_save, weak=False, sender=Project)
def create_payout_for_fully_funded_project(sender, instance, created, **kwargs):

    project = instance
    now = timezone.now()

    # Check projects in phase Act that have asked for money.
    # import ipdb; ipdb.set_trace()
    if project.phase == ProjectPhases.act and project.projectcampaign.money_asked:
        if now.day <= 15:
            next_date = timezone.datetime(now.year, now.month, 15)
        else:
            next_date = timezone.datetime(now.year, now.month, 1) + relativedelta(months=1)

        if project.projectcampaign.money_donated >= project.projectcampaign.money_asked:
            # Fully funded, set payout rule to 5
            payout_rule = PayoutRules.five
        else:
            payout_rule = PayoutRules.twelve

        amount_raised = money_from_cents(
            project.projectcampaign.money_donated
        )
        try:
            # Update existing Payout
            payout = Payout.objects.get(project=project)

            if payout.status == PayoutLineStatuses.new:
                # Update planned payout date for new Payouts
                payout.planned = next_date
                payout.save()

        except Payout.DoesNotExist:

            # Create new Payout
            payout = Payout.objects.create(
                planned=next_date,
                project=project,
                status=PayoutLineStatuses.new,
                amount_raised=amount_raised,
                payout_rule=payout_rule
            )

            organization = project.projectplan.organization
            payout.receiver_account_bic = organization.account_bic
            payout.receiver_account_iban = organization.account_iban
            payout.receiver_account_number = organization.account_number
            payout.receiver_account_name = organization.account_name
            payout.receiver_account_city = organization.account_city
            payout.receiver_account_country = organization.account_bank_country
            payout.invoice_reference = 'PP'
            payout.save()
            payout.invoice_reference = str(project.id) + '-' + str(payout.id)
            payout.save()


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

