from decimal import Decimal
from apps.projects.models import Project, ProjectPhases
from apps.sepa.sepa import SepaDocument
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext as _
from django_countries.fields import CountryField
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem


class Payout(models.Model):
    """
        A projects is payed after it's fully funded in the first batch (2x/month).
        Project payouts are checked manually. Selected projects can be exported to a SEPA file.
    """

    class PayoutLineStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        progress = ChoiceItem('progress', label=_("Progress"))
        completed = ChoiceItem('completed', label=_("Completed"))

    planned = models.DateField(_("Planned"), help_text=_("Date that this batch should be processed."))

    project = models.ForeignKey('projects.Project')

    status = models.CharField(_("status"), max_length=20, choices=PayoutLineStatuses.choices)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))
    amount = models.PositiveIntegerField(_("Amount"))
    currency = models.CharField(_("Currency"), max_length=3)

    sender_account_number = models.CharField(max_length=100)
    receiver_account_number = models.CharField(max_length=100)
    receiver_account_iban = models.CharField(max_length=100)
    receiver_account_bic = models.CharField(max_length=100)
    receiver_account_name = models.CharField(max_length=100)
    receiver_account_city = models.CharField(max_length=100)
    receiver_account_country = models.CharField(max_length=100, null=True)

    invoice_reference = models.CharField(max_length=100)
    description_line1 = models.CharField(max_length=100, blank=True, default="")
    description_line2 = models.CharField(max_length=100, blank=True, default="")
    description_line3 = models.CharField(max_length=100, blank=True, default="")
    description_line4 = models.CharField(max_length=100, blank=True, default="")

    @property
    def local_amount(self):
        return '%.2f' % (float(self.amount) / 100)

    @property
    def local_amount_safe(self):
        return '%.2f' % (self.project.money_safe * settings.PROJECT_PAYOUT_RATE / 100)

    @property
    def is_valid(self):
        # TODO: Do a more advanced check. Maybe use IBAN check by a B. Q. Konrath?
        if self.receiver_account_iban and self.receiver_account_bic:
            return True
        return False

    def __unicode__(self):
        date = self.created.strftime('%d-%m-%Y')
        return  date + " : " + self.receiver_account_number + " : EUR " + str(self.local_amount)


# make this a recurring task
def create_upcoming_payouts():
    now = timezone.now()
    if now.day <= 15:
        next_date = timezone.datetime(now.year, now.month, 15)
    else:
        next_date = timezone.datetime(now.year, now.month + 1, 1)

    projects = Project.objects.filter(payout_date__isnull=True, phase=ProjectPhases.act).all()
    i = 0
    day = timezone.datetime.strftime(now, '%d%m%Y')
    for project in projects:

        i += 1
        invoice_id = day + '-' + str(i)

        amount = round(project.money_donated * settings.PROJECT_PAYOUT_RATE)
        try:
            line = Payout.objects.get(project=project)
            if line.status == Payout.PayoutLineStatuses.new:
                line.planned = next_date
                line.save()
        except Payout.DoesNotExist:
            line = Payout.objects.create(planned=next_date, project=project, status=Payout.PayoutLineStatuses.new,
                                         amount=amount)

            organization = project.organization
            line.receiver_account_bic = organization.account_bic
            line.receiver_account_iban = organization.account_iban
            line.receiver_account_number = organization.account_number
            line.receiver_account_name = organization.account_name
            line.receiver_account_city = organization.account_city
            line.receiver_account_country = organization.account_bank_country
            line.invoice_reference = 'Donations 1%CLUB ' + invoice_id
            line.save()


def create_sepa_xml(payouts):
    batch_id = timezone.datetime.strftime(timezone.now(), '%Y%m%d%H%I%S')
    sepa = SepaDocument(is_test=True, debtor_iban=settings.SEPA['iban'], debtor_bic=settings.SEPA['bic'],
                initiating_party_name=settings.SEPA['name'], initiating_party_id=settings.SEPA['id'],
                message_identification=batch_id, payment_info_id=batch_id)
    for line in payouts.all():
        sepa.add_credit_transfer(amount=line.amount, creditor_payment_id=line.invoice_reference,
                                 creditor_bic=line.receiver_account_bic, creditor_name=line.receiver_account_name,
                                 creditor_iban=line.receiver_account_iban)
    return sepa.as_xml()

