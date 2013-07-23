from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from .models import Donation, Order, OrderItem, Voucher, CustomVoucherRequest
from django.core.urlresolvers import reverse


class DonationAdmin(admin.ModelAdmin):
    model = Donation
    date_hierarchy = 'created'
    list_display = ('created', 'project', 'user', 'local_amount', 'status', 'donation_type')
    list_filter = ('status',)
    raw_id_fields = ('user', 'project')
    readonly_fields = ('donation_type', 'amount', 'currency', 'view_order')
    fields = readonly_fields + ('status', 'user', 'project')
    search_fields = (
        'user__first_name', 'user__last_name', 'project__title'
    )

    def view_order(self, obj):
        donation_type = ContentType.objects.get_for_model(obj)
        object = OrderItem.objects.filter(object_id=obj.id).filter(content_type=donation_type).get()
        object = object.order
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id])
        return "<a href='%s'>View Order</a>" % (str(url))

    view_order.allow_tags = True

admin.site.register(Donation, DonationAdmin)


class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_filter = ('status', 'recurring')
    list_display = ('created', 'total', 'status', 'recurring')
    raw_id_fields = ('user', )
    readonly_fields = ('recurring', 'view_payment')
    fields = readonly_fields + ('user', 'status')

    def view_payment(self, obj):
        object = obj.payments.get()
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id])
        return "<a href='%s'>View Payment</a>" % (str(url))

    view_payment.allow_tags = True

admin.site.register(Order, OrderAdmin)


class VoucherAdmin(admin.ModelAdmin):
    model = Voucher
    list_filter = ('status',)
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

