from apps.cowry_docdata.models import DocDataPayment
from django.contrib import admin
from .models import DocDataPaymentOrder


class DocDataPaymentInline(admin.StackedInline):
    list_display = ('created', 'amount', 'currency', 'status')
    model = DocDataPayment
    extra = 0


class DocDataPaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('created', 'amount', 'currency', 'status')
    model = DocDataPaymentOrder
    inlines = (DocDataPaymentInline,)


admin.site.register(DocDataPaymentOrder, DocDataPaymentOrderAdmin)
