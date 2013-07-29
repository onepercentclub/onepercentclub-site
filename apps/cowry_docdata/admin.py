from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import DocDataPaymentOrder, DocDataPayment, DocDataPaymentLogEntry


class DocDataPaymentLogEntryInine(admin.TabularInline):
    model = DocDataPaymentLogEntry
    can_delete = False
    extra = 0
    max_num = 0
    fields = ('timestamp', 'type', 'level', 'message')
    readonly_fields = fields


class DocDataPaymentInline(admin.TabularInline):
    model = DocDataPayment
    extra = 0


class DocDataPaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('created', 'amount', 'currency', 'status')
    inlines = (DocDataPaymentInline, DocDataPaymentLogEntryInine)

admin.site.register(DocDataPaymentOrder, DocDataPaymentOrderAdmin)


class DocDataPaymentLogEntryAdmin(admin.ModelAdmin):
    model = DocDataPaymentLogEntry

    # List view.
    list_display = ('payment', 'type', 'level', 'message')
    list_filter = ('type', 'level', 'timestamp')
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