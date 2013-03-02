from django.contrib import admin
from .models import Donation, Order, OrderItem, Voucher, CustomVoucherRequest


class DonationAdmin(admin.ModelAdmin):
    model = Donation
    date_hierarchy = 'created'
    list_display = ('created', 'user', 'amount')
    list_filter = ('status', 'project', 'user')

    search_fields = (
        'user__first_name', 'user__last_name', 'project__title'
    )


admin.site.register(Donation, DonationAdmin)


class OrderItemInline(admin.StackedInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_filter = ('status', 'user')
    list_display = ('created', 'amount', 'status')
    inlines = (OrderItemInline, )


admin.site.register(Order, OrderAdmin)


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_filter = ('status', 'sender')
    list_display = ('created', 'amount_euro', 'status', 'sender', 'sender_email', 'receiver_email')


admin.site.register(Voucher, VoucherAdmin)


class CustomVoucherRequestAdmin(admin.ModelAdmin):
    model = Voucher
    list_filter = ('status', 'organization')
    list_display = ('created', 'amount', 'status', 'contact_name', 'contact_email', 'organization')


admin.site.register(CustomVoucherRequest, CustomVoucherRequestAdmin)

