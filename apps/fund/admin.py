from apps.cowry_docdata.models import DocDataPaymentOrder, payment_method_mapping
from babel.numbers import format_currency
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.templatetags.admin_static import static
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from .models import Donation, Order, RecurringDirectDebitPayment, OrderStatuses, DonationStatuses


# http://stackoverflow.com/a/16556771
class DonationStatusFilter(SimpleListFilter):
    title = _('Status')

    parameter_name = 'status__exact'
    default_status = DonationStatuses.paid

    def lookups(self, request, model_admin):
        return (('all', _('All')),) + DonationStatuses.choices

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup if self.value() else lookup == self.default_status,
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() in DonationStatuses.values:
            return queryset.filter(status=self.value())
        elif self.value() is None:
            return queryset.filter(status=self.default_status)


payment_method_icon_mapping = {
    'iDeal': 'fund/icon-ideal.svg',
    'Direct debit': 'fund/icon-direct-debit.png',
    'Mastercard': 'fund/icon-mastercard.svg',
    'Visa': 'fund/icon-visa.svg',
}


class DonationAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated'
    list_display = ('updated', 'ready', 'project', 'user', 'amount_override', 'status', 'type', 'payment_method_override')
    list_filter = (DonationStatusFilter, 'donation_type')
    ordering = ('-ready', '-updated')
    raw_id_fields = ('user', 'project')
    readonly_fields = ('view_order', 'created', 'updated', 'ready')
    fields = readonly_fields + ('status', 'donation_type', 'amount', 'currency', 'user', 'project')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'project__title')

    def view_order(self, obj):
        url = reverse('admin:%s_%s_change' % (obj.order._meta.app_label, obj.order._meta.module_name), args=[obj.order.id])
        return "<a href='%s'>View Order</a>" % (str(url))

    view_order.allow_tags = True

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

    def type(self, obj):
        recurring = obj.donation_type == Donation.DonationTypes.recurring
        icon_url = static(
            'fund/icon-{0}.svg'.format({True: 'recurring-donation', False: 'one-time-donation'}[recurring]))
        alt_text = {True: 'Recurring', False: 'One-time'}[recurring]
        return '<img alt="{0}" src="{1}" height="16px" />'.format(alt_text, icon_url)

    type.allow_tags = True
    type.short_description = 'type'

    def payment_method_override(self, obj):
        payment_method = payment_method_mapping[obj.payment_method]

        if payment_method in payment_method_icon_mapping:
            icon_url = static(payment_method_icon_mapping[payment_method])
            return '<img src="{0}" height="16px" />&nbsp;{1}'.format(icon_url, payment_method)
        return payment_method

    payment_method_override.allow_tags = True
    payment_method_override.short_description = 'payment method'

admin.site.register(Donation, DonationAdmin)


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


class DonationAdminInline(admin.TabularInline):
    model = Donation
    extra = 0
    raw_id_fields = ('project',)
    fields = ('project', 'status', 'amount_override', 'amount', 'currency')
    readonly_fields = ('amount_override',)

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

    class Media:
        css = {"all": ("css/admin/hide_admin_original.css",)}


# TODO Implement this when vouchers are added to the site.
#class VoucherAdminInline(admin.TabularInline):
#    model = Voucher
#    extra = 0
#    raw_id_fields = ('sender',)


class OrderAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated'
    list_filter = (OrderStatusFilter, 'recurring')
    list_display = ('order_number', 'updated', 'closed', 'user',  'total', 'status', 'type', 'payment_status')
    ordering = ('-closed', '-updated')
    raw_id_fields = ('user',)
    readonly_fields = ('total', 'order_number', 'created', 'updated')
    fields = ('recurring',) + readonly_fields + ('user', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'order_number')
    inlines = (DonationAdminInline, DocDataPaymentOrderInline,)

    def total(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.total / 100.0, 'EUR', locale=language)

    def type(self, obj):
        icon_url = static(
            'fund/icon-{0}.svg'.format({True: 'recurring-donation', False: 'one-time-donation'}[obj.recurring]))
        alt_text = {True: 'Recurring', False: 'One-time'}[obj.recurring]
        return '<img alt="{0}" src="{1}" height="16px" />'.format(alt_text, icon_url)


    def payment_status(self, obj):
        if obj.latest_payment:
            return obj.latest_payment.status
        return '-'

    type.allow_tags = True
    type.short_description = 'type'

admin.site.register(Order, OrderAdmin)


# http://stackoverflow.com/a/16556771
class ActiveFilter(SimpleListFilter):
    title = _('Active')

    parameter_name = 'active__exact'
    active_choices = (('1', _('Yes')),
                      ('0', _('No')),)
    default = '1'

    def lookups(self, request, model_admin):
        return (('all', _('All')),) + self.active_choices

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup if self.value() else lookup == self.default,
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() in ('0', '1'):
            return queryset.filter(active=self.value())
        elif self.value() is None:
            return queryset.filter(active=self.default)


class RecurringDirectDebitPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'active', 'amount_override')
    list_filter = (ActiveFilter,)
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name', 'account', 'iban', 'bic')
    raw_id_fields = ('user',)
    readonly_fields = ('created', 'updated')

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

admin.site.register(RecurringDirectDebitPayment, RecurringDirectDebitPaymentAdmin)
