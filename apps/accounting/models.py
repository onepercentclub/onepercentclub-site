from bluebottle.payments_docdata.models import DocdataPayment, DocdataDirectdebitPayment
from django.db import models
from django.utils.translation import ugettext as _
from djchoices import DjangoChoices, ChoiceItem


class BankTransactionCategory(models.Model):

    name = models.CharField(_('Name'), max_length=100)

    def __unicode__(self):
        return self.name

    class Meta():
        verbose_name = _('Bank transaction category')
        verbose_name_plural = _('Bank transaction categories')


class BankTransaction(models.Model):
    """ Rabobank transaction as incrementally imported from CSV. """

    class IntegrityStatus(DjangoChoices):
        Valid = ChoiceItem('valid', _('Valid'))
        UnknownTransaction = ChoiceItem('unknown', _('Invalid: Unknown transaction'))
        AmountMismatch = ChoiceItem('mismatch', _('Invalid: Amount mismatch'))

    class CreditDebit(DjangoChoices):
        credit = ChoiceItem('C', label=_('Credit'))
        debit = ChoiceItem('D', label=_('Debit'))

    category = models.ForeignKey(BankTransactionCategory, blank=True, null=True)
    payout = models.ForeignKey('payouts.ProjectPayout', verbose_name=_('Campaign payout'), blank=True, null=True)
    remote_payout = models.ForeignKey('accounting.RemoteDocdataPayout', verbose_name=_('Docdata payout'), blank=True, null=True)
    remote_payment = models.ForeignKey('accounting.RemoteDocdataPayment', verbose_name=_('Docdata payment'), blank=True, null=True)

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

    filler = models.CharField(_('filler'), max_length=6, blank=True)

    description1 = models.CharField(_('description 1'), max_length=35, blank=True)
    description2 = models.CharField(_('description 2'), max_length=35, blank=True)
    description3 = models.CharField(_('description 3'), max_length=35, blank=True)
    description4 = models.CharField(_('description 4'), max_length=35, blank=True)
    description5 = models.CharField(_('description 5'), max_length=35, blank=True)
    description6 = models.CharField(_('description 6'), max_length=35, blank=True)

    end_to_end_id = models.CharField(_('End to end ID'), max_length=35, blank=True)
    id_recipient = models.CharField(_('ID recipient account'), max_length=35, blank=True)
    mandate_id = models.CharField(_('Mandate ID'), max_length=35, blank=True)

    status = models.CharField(_('status'), max_length=30, blank=True, choices=IntegrityStatus.choices,
                              help_text=_('Cached status assigned during matching.'))
    status_remarks = models.CharField(_('status remarks'), max_length=250, blank=True, help_text=_(
        'Additional remarks regarding the status.'
    ))

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


class RemoteDocdataPayout(models.Model):
    """ Payout to bank account as incrementally imported from CSV. """

    payout_reference = models.CharField(_('Payout Reference'), max_length=100, unique=True)
    payout_date = models.DateField(_('Payout date'), db_index=True, blank=True, null=True)
    start_date = models.DateField(_('Start date'), db_index=True, blank=True, null=True)
    end_date = models.DateField(_('End date'), db_index=True, blank=True, null=True)
    collected_amount = models.DecimalField(
        _('Collected amount'), max_digits=14, decimal_places=2, blank=True, null=True
    )
    payout_amount = models.DecimalField(
        _('Payout amount'), max_digits=14, decimal_places=2, blank=True, null=True
    )

    def __unicode__(self):
        return self.payout_reference

    class Meta:
        ordering = ('-payout_date', )


class RemoteDocdataPayment(models.Model):
    """ Docdata payment as incrementally imported from CSV. """
    class IntegrityStatus(DjangoChoices):
        Valid = ChoiceItem('valid', _('Valid'))
        MissingBackofficeRecord = ChoiceItem('missing', _('Invalid: Missing backoffice record'))
        AmountMismatch = ChoiceItem('mismatch', _('Invalid: Amount mismatch'))

    merchant_reference = models.CharField(
        _('merchant reference'), max_length=35, db_index=True
    )
    triple_deal_reference = models.CharField(
        _('Triple Deal reference'), max_length=40, db_index=True
    )
    payment_type = models.CharField(_('type'), max_length=15, db_index=True)
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

    local_payment = models.ForeignKey('payments.Payment', null=True)
    remote_payout = models.ForeignKey('accounting.RemoteDocdataPayout', null=True)

    status = models.CharField(_('status'), max_length=30, blank=True, choices=IntegrityStatus.choices,
                              help_text=_('Cached status assigned during matching.'))
    status_remarks = models.CharField(_('status remarks'), max_length=250, blank=True, help_text=_(
        'Additional remarks regarding the status.'
    ))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.local_payment and self.merchant_reference:
            try:
                self.local_payment = DocdataPayment.objects.get(payment_cluster_id=self.merchant_reference)
            except DocdataPayment.DoesNotExist:
                try:
                    self.local_payment = DocdataDirectdebitPayment.objects.get(merchant_order_id=self.merchant_reference)
                except DocdataDirectdebitPayment.DoesNotExist:
                    pass
        return super(RemoteDocdataPayment, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.triple_deal_reference

    class Meta:
        ordering = ('-remote_payout__payout_date', )
