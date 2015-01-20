from datetime import date
from djchoices import DjangoChoices, ChoiceItem
from django.db.models import F, Q

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class YesOrNo(DjangoChoices):
    yes = ChoiceItem('1', _('Yes'))
    no = ChoiceItem('0', _('No'))


class DocdataPaymentIntegrityListFilter(SimpleListFilter):
    title = _('integrity status')
    parameter_name = 'integrity'

    class Status(DjangoChoices):
        valid = ChoiceItem('valid', _('Valid'))
        invalid = ChoiceItem('invalid', _('Invalid (all)'))
        missing_local = ChoiceItem('missing_local', _('Invalid: Missing local payment'))
        amount_mismatch = ChoiceItem('amount_mismatch', _('Invalid: Amount mismatch'))

    def lookups(self, request, model_admin):
        return self.Status.choices

    def queryset(self, request, queryset):
        if self.value() == self.Status.valid:
            return queryset.exclude(local_payment=None).filter(local_payment__order_payment__amount=F('amount_collected'))
        if self.value() == self.Status.invalid:
            return queryset.exclude(local_payment__order_payment__amount=F('amount_collected'))
        if self.value() == self.Status.missing_local:
            return queryset.filter(local_payment=None)
        if self.value() == self.Status.amount_mismatch:
            return queryset.exclude(local_payment=None).exclude(local_payment__order_payment__amount=F('amount_collected'))


class DocdataPaymentMatchedListFilter(SimpleListFilter):
    title = _('matched')
    parameter_name = 'matched'

    def lookups(self, request, model_admin):
        return YesOrNo.choices

    def queryset(self, request, queryset):
        if self.value() == YesOrNo.yes:
            return queryset.filter(local_payment__merchant_order_id=F('merchant_reference'))
        if self.value() == YesOrNo.no:
            return queryset.exclude(local_payment__merchant_order_id=F('merchant_reference'))


class BankTransactionMatchedListFilter(SimpleListFilter):
    title = _('matched amount')
    parameter_name = 'matched_amount'

    class Status(DjangoChoices):
        valid = ChoiceItem('valid', _('Valid'))
        invalid = ChoiceItem('invalid', _('Invalid (all)'))
        amount_mismatch = ChoiceItem('amount_mismatch', _('Invalid: Amount mismatch'))
        unknown_transaction = ChoiceItem('unknown_transaction', _('Invalid: Unknown transaction'))

    def lookups(self, request, model_admin):
        return self.Status.choices

    def queryset(self, request, queryset):
        if self.value() == self.Status.valid:
            return queryset.filter(
                Q(remote_payout__payout_amount=F('amount')) |
                Q(payout__amount_payable=F('amount'))
            )
        if self.value() == self.Status.invalid:
            return queryset.filter(
                ~Q(remote_payout__payout_amount=F('amount')) &
                ~Q(payout__amount_payable=F('amount'))
            )
        if self.value() == self.Status.unknown_transaction:
            return queryset.filter(remote_payout=None, payout=None)
        if self.value() == self.Status.amount_mismatch:
            return queryset.exclude(remote_payout=None, payout=None).filter(
                ~Q(remote_payout__payout_amount=F('amount')) &
                ~Q(payout__amount_payable=F('amount'))
            )


class OrderPaymentIntegrityListFilter(SimpleListFilter):
    title = _('integrity status')
    parameter_name = 'integrity'

    class Status(DjangoChoices):
        valid = ChoiceItem('valid', _('Valid'))
        invalid = ChoiceItem('invalid', _('Invalid (all)'))
        missing_rdp = ChoiceItem('missing_rdp', _('Invalid: Missing remote payment'))
        amount_mismatch = ChoiceItem('amount_mismatch', _('Invalid: Amount mismatch'))

    def lookups(self, request, model_admin):
        return self.Status.choices

    def queryset(self, request, queryset):
        if self.value() == self.Status.valid:
            return queryset.exclude(payment=None).filter(rdp_amount_collected=F('amount'))
        if self.value() == self.Status.invalid:
            return queryset.filter(
                Q(payment=None) |
                Q(payment__remotedocdatapayment=None) |
                ~Q(rdp_amount_collected=F('amount'))
            )
        if self.value() == self.Status.missing_rdp:
            return queryset.filter(
                Q(payment=None) |
                Q(payment__remotedocdatapayment=None)
            )
        if self.value() == self.Status.amount_mismatch:
            return queryset.filter(
                ~Q(rdp_amount_collected=F('amount'))
            )


class OrderPaymentMatchedListFilter(SimpleListFilter):
    title = _('matched')
    parameter_name = 'matched'

    def lookups(self, request, model_admin):
        return YesOrNo.choices

    def queryset(self, request, queryset):
        if self.value() == YesOrNo.yes:
            return queryset.filter(payment__remotedocdatapayment__merchant_reference=F('payment__docdatapayment__merchant_order_id'))
        if self.value() == YesOrNo.no:
            return queryset.exclude(payment__remotedocdatapayment__merchant_reference=F('payment__docdatapayment__merchant_order_id'))
