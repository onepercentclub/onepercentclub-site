from babel.numbers import format_currency
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import translation
from .models import DocDataPaymentOrder, DocDataPayment, DocDataPaymentLogEntry


class DocDataPaymentLogEntryInine(admin.TabularInline):
    model = DocDataPaymentLogEntry
    can_delete = False
    extra = 0
    max_num = 0
    fields = ('timestamp', 'level', 'message')
    readonly_fields = fields


class DocDataPaymentInline(admin.TabularInline):
    model = DocDataPayment
    can_delete = False
    extra = 0
    max_num = 0
    fields = ('payment_method', 'status', 'created', 'updated')
    readonly_fields = fields


class DocDataPaymentOrderAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('created', 'amount_override', 'status')
    raw_id_fields = ('order',)
    search_fields = ('payment_order_id', 'merchant_order_reference')
    inlines = (DocDataPaymentInline, DocDataPaymentLogEntryInine)

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100, obj.currency, locale=language)

    amount_override.short_description = 'amount'

admin.site.register(DocDataPaymentOrder, DocDataPaymentOrderAdmin)


class DocDataPaymentLogEntryAdmin(admin.ModelAdmin):
    # List view.
    list_display = ('payment', 'level', 'message')
    list_filter = ('level', 'timestamp')
    search_fields = ('message',)

    def payment(self, obj):
        payment = obj.docdata_payment_order
        url = reverse('admin:%s_%s_change' % (payment._meta.app_label, payment._meta.module_name), args=[payment.id])
        return "<a href='%s'>%s</a>" % (str(url), payment)

    payment.allow_tags = True

    # Don't allow the detail view to be accessed.
    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return False

admin.site.register(DocDataPaymentLogEntry, DocDataPaymentLogEntryAdmin)
