from apps.cowry_docdata.models import DocDataPaymentOrder
from babel.numbers import format_currency
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.templatetags.admin_static import static
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from .models import Donation, Order, OrderItem, Voucher, CustomVoucherRequest, RecurringDirectDebitPayment, \
    OrderStatuses


class DonationAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('created', 'project', 'user', 'amount_override', 'status', 'type', 'payment_method')
    list_filter = ('status',)
    raw_id_fields = ('user', 'project')
    readonly_fields = ('view_order',)
    fields = readonly_fields + ('status', 'donation_type', 'amount', 'currency', 'user', 'project')
    search_fields = ('user__first_name', 'user__last_name', 'project__title')

    def view_order(self, obj):
        donation_type = ContentType.objects.get_for_model(obj)
        donation = OrderItem.objects.filter(object_id=obj.id).filter(content_type=donation_type).get()
        order = donation.order
        url = reverse('admin:%s_%s_change' % (order._meta.app_label, order._meta.module_name),  args=[order.id])
        return "<a href='%s'>View Order</a>" % (str(url))

    view_order.allow_tags = True

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

    def type(self, obj):
        recurring = obj.donation_type == Donation.DonationTypes.recurring
        icon_url = static(
            'fund/icon-{0}.png'.format({True: 'recurring-donation', False: 'one-time-donation'}[recurring]))
        alt_text = {True: 'Recurring', False: 'One-time'}[recurring]
        return '<img alt="{0}" src="{1}" />'.format(alt_text, icon_url)

    type.allow_tags = True
    type.short_description = 'type'

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
    fields = ('payment', 'amount_override', 'status',)
    readonly_fields = fields

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

    def payment(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.module_name), args=[obj.id])
        return "<a href='%s'>%s</a>" % (str(url), obj)

    payment.allow_tags = True


# Inspiration from:
# http://stackoverflow.com/a/16556771
class OrderStatusFilter(SimpleListFilter):
    title = _('Status')

    parameter_name = 'status__exact'
    default_status = OrderStatuses.closed

    def lookups(self, request, model_admin):
        return (('all', _('All')),) + OrderStatuses.choices

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup if self.value() else lookup == self.default_status,
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() in OrderStatuses.values:
            return queryset.filter(status=self.value())
        elif self.value() is None:
            return queryset.filter(status=self.default_status)


class OrderAdmin(admin.ModelAdmin):
    list_filter = (OrderStatusFilter, 'recurring')
    list_display = ('order_number', 'user', 'created', 'updated', 'total', 'status', 'type')
    raw_id_fields = ('user',)
    readonly_fields = ('type', 'total', 'order_number', 'created', 'updated')
    fields = readonly_fields + ('user', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'order_number')
    inlines = (OrderItemInline, DocDataPaymentOrderInline,)

    def total(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.total / 100.0, 'EUR', locale=language)

    def type(self, obj):
        icon_url = static(
            'fund/icon-{0}.png'.format({True: 'recurring-donation', False: 'one-time-donation'}[obj.recurring]))
        alt_text = {True: 'Recurring', False: 'One-time'}[obj.recurring]
        return '<img alt="{0}" src="{1}" />'.format(alt_text, icon_url)

    type.allow_tags = True
    type.short_description = 'type'

admin.site.register(Order, OrderAdmin)


class VoucherAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('created', 'amount_override', 'status', 'sender_email', 'receiver_email')
    readonly_fields = ('sender', 'receiver', 'donations')
    fields = readonly_fields + ('status', 'amount', 'currency', 'code', 'sender_email', 'receiver_email',
                                'receiver_name', 'sender_name', 'message')

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

admin.site.register(Voucher, VoucherAdmin)


class CustomVoucherRequestAdmin(admin.ModelAdmin):
    list_filter = ('status', 'organization')
    list_display = ('created', 'number', 'status', 'contact_name', 'contact_email', 'organization')

admin.site.register(CustomVoucherRequest, CustomVoucherRequestAdmin)


class RecurringDirectDebitPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'active', 'amount_override')
    list_filter = ('active',)
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name', 'account', 'iban', 'bic')
    raw_id_fields = ('user',)
    readonly_fields = ('created', 'updated')

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

admin.site.register(RecurringDirectDebitPayment, RecurringDirectDebitPaymentAdmin)
