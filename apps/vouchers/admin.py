from apps.fund.admin import DonationAdminInline
from babel.numbers import format_currency
from django.contrib import admin
from django.utils import translation
from .models import CustomVoucherRequest, Voucher


class VoucherAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('created', 'amount_override', 'status', 'sender_email', 'receiver_email')
    readonly_fields = ('sender', 'receiver')
    fields = readonly_fields + ('status', 'amount', 'currency', 'code', 'sender_email', 'receiver_email',
                                'receiver_name', 'sender_name', 'message')
    inlines = (DonationAdminInline,)

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

admin.site.register(Voucher, VoucherAdmin)


class CustomVoucherRequestAdmin(admin.ModelAdmin):
    list_filter = ('status', 'organization')
    list_display = ('created', 'number', 'status', 'contact_name', 'contact_email', 'organization')

admin.site.register(CustomVoucherRequest, CustomVoucherRequestAdmin)