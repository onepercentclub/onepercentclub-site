from django.db import models
from django.utils.translation import ugettext as _

from djchoices import DjangoChoices, ChoiceItem


class BankTransaction(models.Model):
    """ Rabobank transaction as incrementally imported from CSV. """

    class CreditDebit(DjangoChoices):
        credit = ChoiceItem('C', label=_('Credit'))
        debit = ChoiceItem('D', label=_('Debit'))

    sender_account = models.CharField(_('holder account number'), max_length=35)
    currency = models.CharField(_('currency'), max_length=3)
    interest_date = models.DateField(_('interest date'))
    credit_debit = models.CharField(
        _('credit/debit'), max_length=1, db_index=True,
        choices=CreditDebit.choices
    )
    amount = models.DecimalField(_('amount'), max_digits=14, decimal_places=2)
    counter_account = models.CharField(_('recipient account'), max_length=35)
    counter_name = models.CharField(_('recipient name'), max_length=70)
    book_date = models.DateField(_('book date'), db_index=True)
    book_code = models.CharField(_('book code'), max_length=2)

    filler = models.CharField(_('filler'), max_length=6)

    description1 = models.CharField(_('description 1'), max_length=35)
    description2 = models.CharField(_('description 2'), max_length=35)
    description3 = models.CharField(_('description 3'), max_length=35)
    description4 = models.CharField(_('description 4'), max_length=35)
    description5 = models.CharField(_('description 5'), max_length=35)
    description6 = models.CharField(_('description 6'), max_length=35)

    end_to_end_id = models.CharField(_('End to end ID'), max_length=35)
    id_recipient = models.CharField(_('ID recipient account'), max_length=35)
    mandate_id = models.CharField(_('Mandate ID'), max_length=35)

    class Meta:
        verbose_name = _('bank transaction')
        verbose_name_plural = _('bank transactions')

    def __unicode__(self):
        if self.credit_debit == self.CreditDebit.credit:
            return _('%s from %s') % (
                self.amount, self.counter_name or self.counter_account
            )
        else:
            return _('%s to %s') % (
                self.amount, self.counter_name or self.counter_account
            )


class DocdataPayout(models.Model):
    """ Payout to bank account as incrementally imported from CSV. """

    period_id = models.PositiveIntegerField(_('period ID'), unique=True)
    start_date = models.DateField(_('start date'), db_index=True)
    end_date = models.DateField(_('end date'), db_index=True)
    total = models.DecimalField(
        _('total'), max_digits=14, decimal_places=2, blank=True, null=True
    )

    class Meta:
        verbose_name = _('Docdata payout')
        verbose_name_plural = _('Docdata payouts')


class DocdataPayment(models.Model):
    """ Docdata payment as incrementally imported from CSV. """

    merchant_reference = models.CharField(
        _('merchant reference'), max_length=35, db_index=True
    )
    triple_deal_reference = models.PositiveIntegerField(
        _('Triple Deal reference'), db_index=True
    )
    payment_type = models.CharField(_('type'), max_length=15, db_index=True)
    amount_registered = models.DecimalField(
        _('amount registered'), max_digits=14, decimal_places=2
    )
    currency_amount_registered = models.CharField(
        _('currency of amount registered'), max_length=3
    )
    amount_collected = models.DecimalField(
        _('amount collected'), max_digits=14, decimal_places=2
    )
    currency_amount_collected = models.CharField(
        _('currency of amount collected'), max_length=3
    )
    tpcd = models.DecimalField(
        _('TPCD'), max_digits=14, decimal_places=2, blank=True, null=True
    )
    currency_tpcd = models.CharField(
        _('currency of TPCD'), max_length=3, blank=True
    )
    tpci = models.DecimalField(
        _('TPCI'), max_digits=14, decimal_places=2, blank=True, null=True
    )
    currency_tpci = models.CharField(
        _('currency of TPCI'), max_length=3, blank=True
    )
    docdata_fee = models.DecimalField(
        _('Docdata payments fee'), max_digits=14, decimal_places=2
    )
    currency_docdata_fee = models.CharField(
        _('currency of Docdata payments fee'), max_length=3
    )

    class Meta:
        unique_together = (
            'merchant_reference', 'triple_deal_reference', 'payment_type'
        )
        verbose_name = _('Docdata payment')
        verbose_name_plural = _('Docdata payments')

