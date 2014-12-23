from decimal import Decimal
from apps.accounting.models import BankTransactionCategory
from apps.accounting.signals import match_transaction_with_payout
from bluebottle.payments.models import Payment
from bluebottle.utils.utils import StatusDefinition
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext as _

from apps.csvimport.admin import IncrementalCSVImportMixin
from django.core.urlresolvers import reverse

from .models import BankTransaction, RemoteDocdataPayment, RemoteDocdataPayout
from bluebottle.payments_docdata.models import DocdataPayment

from .forms import BankTransactionImportForm, DocdataPaymentImportForm


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


class DocdataPayoutAdmin(admin.ModelAdmin):
    date_hierarchy = 'start_date'

    list_display = ['payout_reference', 'week', 'start_date', 'end_date', 'payout_date', 'payout_amount',
                    'payments_total', 'local_payments_total']

    readonly_fields = ['payout_reference', 'payout_date', 'payout_amount',
                       'start_date', 'end_date', 'collected_amount',
                       'payments_count', 'payments_total', 'fee_total', 'costs_total', 'vat_costs',
                       'local_payments_total', 'local_payments_count']

    fieldsets = (
        (None, {
            'fields': ('payout_reference', 'payout_date', 'payout_amount',
                       'start_date', 'end_date', 'collected_amount')
        }),
        ('Calculated from remote payments', {
            'fields': ('payments_count', 'payments_total', 'fee_total', 'costs_total', 'vat_costs')
        }),
        ('Calculated from local order-payments', {
            'fields': ('local_payments_count', 'local_payments_total', )
        })
    )

    def week(self, obj):
        if obj.start_date:
            return 'Week {0}'.format(obj.start_date.isocalendar()[1])
        return '?'

    def local_payments_total(self, obj):
        return obj.remotedocdatapayment_set.filter(local_payment__order_payment__status=StatusDefinition.SETTLED).aggregate(total=Sum('local_payment__order_payment__amount'))['total']
        payment_ids =  obj.remotedocdatapayment_set.values_list('local_payment_id')
        total = Payment.objects.filter(id__in=payment_ids).aggregate(total=Sum('amount'))
        return total['total']

    def local_payments_count(self, obj):
        payment_ids = obj.remotedocdatapayment_set.values_list('local_payment_id')
        return len(payment_ids)

    def payments_count(self, obj):
        count = obj.remotedocdatapayment_set.count()
        return count

    def payments_count(self, obj):
        count = obj.remotedocdatapayment_set.count()
        url = '/admin/accounting/remotedocdatapayment/'
        return "<a href='{0}?remote_payout__id__exact={1}'>{2} payments</a>".format(url, obj.id, count)

    payments_count.allow_tags = True

    def payments_total(self, obj):
        total = obj.remotedocdatapayment_set.aggregate(total=Sum('amount_collected'))
        return total['total']

    def fee_total(self, obj):
        return obj.remotedocdatapayment_set.aggregate(total=Sum('docdata_fee'))['total']

    def costs_total(self, obj):
        return obj.remotedocdatapayment_set.aggregate(total=Sum('tpci'))['total']

    def vat_costs(self, obj):
        costs = self.costs_total(obj) + self.fee_total(obj)
        return round(costs * 21) / 100


admin.site.register(RemoteDocdataPayout, DocdataPayoutAdmin)


class DocdataPaymentAdmin(IncrementalCSVImportMixin, admin.ModelAdmin):
    list_display = [
        'triple_deal_reference', 'merchant_reference', 'payment_type',
        'matched', 'payment_link', 'integrity_check',
    ]

    list_filter = ['payment_type', ]

    readonly_fields = ['payout_link', 'payment_link', 'merchant_reference', 'triple_deal_reference',
                       'payment_type', 'amount_collected', 'currency_amount_collected', 'tpci', 'docdata_fee', 'integrity_check']

    fields = readonly_fields

    search_fields = ['merchant_reference', 'triple_deal_reference', 'remote_payout__payout_reference']

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

    def integrity_check(self, obj):
        if not obj.local_payment:
            return 'No local payment to conenct to.'
        if obj.local_payment.order_payment.amount == obj.amount_collected:
            return 'ok'
        return 'OrderPayment: {0}.'.format(obj.local_payment.order_payment.amount)

    def payout_link(self, obj):
        object = obj.remote_payout
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object)

    payout_link.allow_tags = True


admin.site.register(RemoteDocdataPayment, DocdataPaymentAdmin)


admin.site.register(BankTransactionCategory)