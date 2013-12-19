from django.contrib import admin

from apps.csvimport.admin import IncrementalCSVImportMixin

from .models import BankTransaction, DocdataPayout, DocdataPayment

from .forms import (
    BankTransactionImportForm, DocdataPayoutImportForm,
    DocdataPaymentImportForm
)


class BankTransactionAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    date_hierarchy = 'book_date'

    search_fields = [
        'counter_account', 'counter_name',
        'description1', 'description2', 'description2', 'description4',
        'description5', 'description6',
        'amount'
    ]

    list_display = [
        'book_date', 'counter_name','counter_account', 'credit_debit', 'amount'
    ]

    list_filter = [
        'credit_debit', 'book_date'
    ]

    import_form = BankTransactionImportForm

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
