from apps.accounting.models import BankTransactionCategory
from apps.accounting.signals import match_transaction_with_payout
from django.contrib import admin
from django.utils.translation import ugettext as _

from apps.csvimport.admin import IncrementalCSVImportMixin
from django.core.urlresolvers import reverse

from .models import BankTransaction, DocdataPayout, DocdataPayment

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

    list_display = ['period_id', 'start_date', 'end_date', 'total']

    import_form = DocdataPayoutImportForm

admin.site.register(DocdataPayout, DocdataPayoutAdmin)


class DocdataPaymentAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    list_display = [
        'triple_deal_reference', 'merchant_reference',
        'amount_registered', 'amount_collected', 'payment_type'
    ]

    list_filter = ['payment_type', ]

    search_fields = ['merchant_reference', 'triple_deal_reference']

    import_form = DocdataPaymentImportForm

admin.site.register(DocdataPayment, DocdataPaymentAdmin)


admin.site.register(BankTransactionCategory)