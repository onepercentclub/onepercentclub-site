from django.contrib import admin
from .models import DocDataPaymentOrder


class DocDataPaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('created', 'amount', 'currency', 'status')
    model = DocDataPaymentOrder

admin.site.register(DocDataPaymentOrder, DocDataPaymentOrderAdmin)
