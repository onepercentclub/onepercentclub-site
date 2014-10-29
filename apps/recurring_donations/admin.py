from apps.recurring_donations.models import MonthlyProject
from .models import MonthlyDonation, MonthlyBatch, MonthlyOrder, MonthlyDonor, MonthlyDonorProject
from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext as _


class MonthlyProjectInline(admin.TabularInline):
    model = MonthlyProject
    readonly_fields = ('project', 'amount', 'fully_funded')
    fields = readonly_fields
    extra = 0
    can_delete = False
    ordering = ('-amount', )

    def has_add_permission(self, request):
        return False

    def fully_funded(self, obj):
        if obj.project.amount_needed <= obj.amount:
            return 'FUNDED'
        return '-'

    class Media:
        css = {"all": ("css/admin/hide_admin_original.css",)}


class MonthlyDonorProjectInline(admin.TabularInline):
    model = MonthlyDonorProject
    raw_id_fields = ('project', )
    fields = ('project', )
    extra = 0


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


class MonthlyDonorAdmin(admin.ModelAdmin):
    model = MonthlyDonor
    list_display = ('user', 'amount', 'active', 'iban', 'selected_projects')
    raw_id_fields = ('user', )
    inlines = (MonthlyDonorProjectInline, )
    list_filter = (ActiveFilter, )
    search_fields = ('user__first_name', 'user__email', 'iban')

    def selected_projects(self, obj):
        return obj.projects.count() or '-'

admin.site.register(MonthlyDonor, MonthlyDonorAdmin)


class MonthlyDonorProjectAdmin(admin.ModelAdmin):
    model = MonthlyDonorProject
    list_display = ('donor', 'project')
    readonly_fields = ('donor', )
    raw_id_fields = ('project', )

admin.site.register(MonthlyDonorProject, MonthlyDonorProjectAdmin)


class MonthlyBatchAdmin(admin.ModelAdmin):
    model = MonthlyBatch
    readonly_fields = ('date', 'monthly_orders')
    inlines = (MonthlyProjectInline, )



    def monthly_orders(self, obj):
        url = '/admin/recurring_donations/monthlyorder?processed__exact={0}&batch={1}'
        return "<a href='{3}'>{0} processed</a><br/><a href='{4}'>{1} unprocessed ({2} errored)</a>".format(
            obj.orders.filter(processed=True).count(),
            obj.orders.filter(processed=False).count(),
            obj.orders.filter(error__gt='').count(),
            url.format(1, obj.id),
            url.format(0, obj.id)
        )

    monthly_orders.allow_tags = True

admin.site.register(MonthlyBatch, MonthlyBatchAdmin)


class MonthlyDonationInline(admin.TabularInline):
    model = MonthlyDonation
    readonly_fields = ('amount', )
    raw_id_fields = ('project', )
    can_delete = False
    fields = ('project', 'amount')
    extra = 0

    def has_add_permission(self, request):
        return False


class MonthlyOrderAdmin(admin.ModelAdmin):
    model = MonthlyDonation
    list_display = ('user', 'amount', 'batch', 'processed', 'has_error')
    readonly_fields = ('user', 'amount', 'batch', 'iban', 'bic', 'name', 'city', 'processed', 'error_message')
    fields = readonly_fields
    list_filter = ('batch', 'processed')
    raw_id_fields = ('user', 'batch')
    inlines = (MonthlyDonationInline, )
    search_fields = ('user__email', )

    ordering = ('-batch', 'user__email')

    def error_message(self, obj):
        return "<span style='color:red; font-weight: bold'>{0}</span>".format(obj.error)

    error_message.allow_tags = True

    def has_error(self, obj):
        if obj.error:
            return "<span style='color:red; font-weight: bold'>ERROR!</span>"
        return '-'

    has_error.allow_tags = True



admin.site.register(MonthlyOrder, MonthlyOrderAdmin)


class MonthlyDonationAdmin(admin.ModelAdmin):
    model = MonthlyDonation
    list_display = ('user', 'project', 'order')
    raw_id_fields = ('user', 'project', 'order')

admin.site.register(MonthlyDonation, MonthlyDonationAdmin)

