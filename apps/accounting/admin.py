from django.contrib import admin

from apps.csvimport.admin import IncrementalCSVImportMixin

from .models import BankTransaction, DocdataPayout, DocdataPayment

from .forms import (
    BankTransactionImportForm, DocdataPayoutImportForm,
    DocdataPaymentImportForm
)


class BankTransactionAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    date_hierarchy = 'book_date'

    import_form = BankTransactionImportForm

admin.site.register(BankTransaction, BankTransactionAdmin)


class DocdataPayoutAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    date_hierarchy = 'start_date'

    list_display = ['period_id', 'start_date', 'end_date', 'total']

    import_form = DocdataPayoutImportForm

admin.site.register(DocdataPayout, DocdataPayoutAdmin)


class DocdataPaymentAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    list_filter = ['payment_type']
    search_fields = ['merchant_reference', 'triple_deal_reference']

    import_form = DocdataPaymentImportForm

admin.site.register(DocdataPayment, DocdataPaymentAdmin)
