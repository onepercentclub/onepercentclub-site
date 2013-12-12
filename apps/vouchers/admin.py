from apps.fund.models import Donation
from babel.numbers import format_currency
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import translation
from .models import CustomVoucherRequest, Voucher


class VoucherDonationInline(admin.StackedInline):
    model = Donation
    raw_id_fields = ('project', 'user')
    readonly_fields = ('amount', )
    fields = readonly_fields + ('project', 'user')
    extra = 0


class VoucherAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    search_fields = ('code', 'sender_email', 'receiver_email')
    list_display = ('created', 'code', 'amount_override', 'status', 'sender_email', 'receiver_email')
    raw_id_fields = ('sender', 'receiver')
    readonly_fields = ('view_order',)
    fields = readonly_fields + ('sender', 'receiver', 'status', 'amount', 'currency', 'code', 'sender_email',
                                'receiver_email', 'receiver_name', 'sender_name', 'message')

    inlines = (VoucherDonationInline, )

    def view_order(self, obj):
        url = reverse('admin:%s_%s_change' % (obj.order._meta.app_label, obj.order._meta.module_name), args=[obj.order.id])
        return "<a href='%s'>View Order</a>" % (str(url))

    view_order.allow_tags = True

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

admin.site.register(Voucher, VoucherAdmin)


class CustomVoucherRequestAdmin(admin.ModelAdmin):
    list_filter = ('status', 'organization')
    list_display = ('created', 'number', 'status', 'contact_name', 'contact_email', 'organization')

admin.site.register(CustomVoucherRequest, CustomVoucherRequestAdmin)