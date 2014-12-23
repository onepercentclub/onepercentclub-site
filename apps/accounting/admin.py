from apps.accounting.models import BankTransactionCategory
from apps.accounting.signals import match_transaction_with_payout
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext as _

from apps.csvimport.admin import IncrementalCSVImportMixin
from django.core.urlresolvers import reverse

from .models import BankTransaction, RemoteDocdataPayment, RemoteDocdataPayout
from bluebottle.payments_docdata.models import DocdataPayment

from .forms import (
    BankTransactionImportForm, DocdataPayoutImportForm,
    DocdataPaymentImportForm
)


class BankTransactionAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    date_hierarchy = 'book_date'

    actions = ('find_matches', )

    search_fields = [
        'counter_account', 'counter_name',
        'description1', 'description2', 'description2', 'description4',
        'description5', 'description6',
        'amount'
    ]

    list_display = [
        'book_date', 'counter_name','counter_account', 'credit_debit', 'amount', 'category'
    ]

    list_filter = [
        'credit_debit', 'book_date', 'category'
    ]
    list_editable = ('category', )

    raw_id_fields = ('payout', )

    readonly_fields = ('payout_link', )

    import_form = BankTransactionImportForm

    def payout_link(self, obj):
        object = obj.payout
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object)

    payout_link.allow_tags = True

    def find_matches(self, request, queryset):
        #
        for transaction in queryset.all():
            match_transaction_with_payout(transaction)

    find_matches.short_description = _("Try to match with payouts.")

admin.site.register(BankTransaction, BankTransactionAdmin)


class DocdataPayoutAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    date_hierarchy = 'start_date'

    list_display = ['payout_reference', 'payout_date', 'payout_amount']

admin.site.register(RemoteDocdataPayout, DocdataPayoutAdmin)


class DocdataPaymentAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    list_display = [
        'triple_deal_reference', 'merchant_reference', 'payment_type',
        'matched', 'payment_link'
    ]

    list_filter = ['payment_type', ]

    readonly_fields = ['payout_link', 'payment_link', 'merchant_reference', 'triple_deal_reference',
                       'payment_type', 'amount_collected']

    fields = readonly_fields

    search_fields = ['merchant_reference', 'triple_deal_reference']

    import_form = DocdataPaymentImportForm

    def payment_link(self, obj):
        payment = obj.local_payment
        if payment:
            payment = DocdataPayment.objects.get(merchant_order_id=obj.merchant_reference)
            url = reverse('admin:%s_%s_change' % (payment._meta.app_label, payment._meta.module_name), args=[payment.id])
            return "<a href='%s'>%s</a>" % (str(url), payment)
        return '-'

    payment_link.allow_tags = True

    def matched(self, obj):
        if DocdataPayment.objects.filter(merchant_order_id=obj.merchant_reference).count():
            return True
        return False

    def payout_link(self, obj):
        object = obj.remote_payout
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object)

    payout_link.allow_tags = True


admin.site.register(RemoteDocdataPayment, DocdataPaymentAdmin)


admin.site.register(BankTransactionCategory)