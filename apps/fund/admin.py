from django.contrib import admin
from .models import Donation, Order, OrderItem, Voucher, CustomVoucherRequest


class DonationAdmin(admin.ModelAdmin):
    model = Donation
    date_hierarchy = 'created'
    list_display = ('created', 'project', 'user', 'local_amount', 'status', 'donation_type')
    list_filter = ('status',)
    search_fields = (
        'user__first_name', 'user__last_name', 'project__title'
    )


admin.site.register(Donation, DonationAdmin)


class OrderItemInline(admin.StackedInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_filter = ('status', 'user')
    list_display = ('created', 'total', 'status')
    inlines = [OrderItemInline, ]


admin.site.register(Order, OrderAdmin)


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_filter = ('status', )
    list_display = ('created', 'amount_euro', 'status', 'sender_email', 'receiver_email')
    readonly_fields = ('sender', 'receiver', 'donations')
    fields = readonly_fields + ('status', 'amount', 'currency', 'code', 'sender_email', 'receiver_email',
                                'receiver_name', 'sender_name', 'message')


admin.site.register(Voucher, VoucherAdmin)


class CustomVoucherRequestAdmin(admin.ModelAdmin):
    model = Voucher
    list_filter = ('status', 'organization')
    list_display = ('created', 'number', 'status', 'contact_name', 'contact_email', 'organization')


admin.site.register(CustomVoucherRequest, CustomVoucherRequestAdmin)

