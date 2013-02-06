from django.contrib import admin
from .models import Payment, PaymentMethod, PaymentAdapter


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("created", "amount", "status")
    model = Payment

admin.site.register(Payment, PaymentAdmin)


class PaymentMethodInline(admin.StackedInline):
    model = PaymentMethod


class PaymentAdapterAdmin(admin.ModelAdmin):
    model = PaymentAdapter
    inlines = (PaymentMethodInline,)


admin.site.register(PaymentAdapter, PaymentAdapterAdmin)

