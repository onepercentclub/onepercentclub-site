from datetime import date
from djchoices import DjangoChoices, ChoiceItem
from django.db.models import F, Q, Sum

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class YesOrNo(DjangoChoices):
    yes = ChoiceItem('1', _('Yes'))
    no = ChoiceItem('0', _('No'))


class DocdataPaymentMatchedListFilter(SimpleListFilter):
    title = _('matched')
    parameter_name = 'matched'

    def lookups(self, request, model_admin):
        return YesOrNo.choices

    def queryset(self, request, queryset):
        if self.value() == YesOrNo.yes:
            return queryset.filter(local_payment__docdatapayment__merchant_order_id=F('merchant_reference'))
        if self.value() == YesOrNo.no:
            return queryset.exclude(local_payment__docdatapayment__merchant_order_id=F('merchant_reference'))


class IntegrityStatusListFilter(SimpleListFilter):
    title = _('integrity status')
    parameter_name = 'integrity'

    class Status(DjangoChoices):
        valid = ChoiceItem('valid', _('Valid'))
        invalid = ChoiceItem('invalid', _('Invalid'))

    def lookups(self, request, model_admin):
        return self.Status.choices

    def queryset(self, request, queryset):
        if self.value() == self.Status.valid:
            return queryset.filter(status=queryset.model.IntegrityStatus.Valid)
        if self.value() == self.Status.invalid:
            return queryset.exclude(status=queryset.model.IntegrityStatus.Valid)


class OrderPaymentIntegrityListFilter(SimpleListFilter):
    title = _('integrity status')
    parameter_name = 'integrity'

    class Status(DjangoChoices):
        valid = ChoiceItem('valid', _('Valid'))
        invalid = ChoiceItem('invalid', _('Invalid'))

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
