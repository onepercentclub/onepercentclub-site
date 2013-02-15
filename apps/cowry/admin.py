from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("created", "amount", "status")
    model = Payment

admin.site.register(Payment, PaymentAdmin)
