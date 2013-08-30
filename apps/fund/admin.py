from apps.cowry_docdata.models import DocDataPaymentOrder
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from .models import Donation, Order, OrderItem, Voucher, CustomVoucherRequest, RecurringDirectDebitPayment


class DonationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('created', 'project', 'user', 'local_amount', 'status', 'donation_type', 'payment_method')
    list_filter = ('status',)
    raw_id_fields = ('user', 'project')
    readonly_fields = ('donation_type', 'amount', 'currency', 'view_order')
    fields = readonly_fields + ('status', 'user', 'project')
    search_fields = ('user__first_name', 'user__last_name', 'project__title')

    def view_order(self, obj):
        donation_type = ContentType.objects.get_for_model(obj)
        donation = OrderItem.objects.filter(object_id=obj.id).filter(content_type=donation_type).get()
        order = donation.order
        url = reverse('admin:%s_%s_change' %(order._meta.app_label,  order._meta.module_name),  args=[order.id])
        return "<a href='%s'>View Order</a>" % (str(url))

    view_order.allow_tags = True

admin.site.register(Donation, DonationAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('type', 'content_object')
    readonly_fields = fields


class DocDataPaymentOrderInline(admin.TabularInline):
    model = DocDataPaymentOrder
    extra = 0
    max_num = 0
    fields = ('payment', 'currency', 'amount', 'status',)
    readonly_fields = fields

    def payment(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=[obj.id])
        return "<a href='%s'>%s</a>" % (str(url), obj)

    payment.allow_tags = True


class OrderAdmin(admin.ModelAdmin):
    list_filter = ('status', 'recurring')
    list_display = ('order_number', 'user', 'created', 'total', 'status', 'recurring')
    raw_id_fields = ('user',)
    readonly_fields = ('recurring', 'total', 'order_number')
    fields = readonly_fields + ('user', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'order_number')
    inlines = (OrderItemInline, DocDataPaymentOrderInline,)

admin.site.register(Order, OrderAdmin)


class VoucherAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('created', 'amount_euro', 'status', 'sender_email', 'receiver_email')
    readonly_fields = ('sender', 'receiver', 'donations')
    fields = readonly_fields + ('status', 'amount', 'currency', 'code', 'sender_email', 'receiver_email',
                                'receiver_name', 'sender_name', 'message')

admin.site.register(Voucher, VoucherAdmin)


class CustomVoucherRequestAdmin(admin.ModelAdmin):
    list_filter = ('status', 'organization')
    list_display = ('created', 'number', 'status', 'contact_name', 'contact_email', 'organization')

admin.site.register(CustomVoucherRequest, CustomVoucherRequestAdmin)


class RecurringDirectDebitPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'active', 'amount', 'currency')
    list_filter = ('active',)
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

admin.site.register(RecurringDirectDebitPayment, RecurringDirectDebitPaymentAdmin)
