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

    def fully_funded(self, obj):
        if obj.project.amount_needed <= obj.amount:
            return 'FUNDED'
        return '-'


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
    list_display = ('id', 'date')
    inlines = (MonthlyProjectInline, )

admin.site.register(MonthlyBatch, MonthlyBatchAdmin)


class MonthlyDonationInline(admin.TabularInline):
    model = MonthlyDonation
    readonly_fields = ('project', 'amount')
    fields = readonly_fields
    extra = 0


class MonthlyOrderAdmin(admin.ModelAdmin):
    model = MonthlyDonation
    list_display = ('user', 'amount', 'batch')
    list_filter = ('batch', )
    raw_id_fields = ('user', 'batch')
    inlines = (MonthlyDonationInline, )
    search_fields = ('user__email', )

admin.site.register(MonthlyOrder, MonthlyOrderAdmin)


class MonthlyDonationAdmin(admin.ModelAdmin):
    model = MonthlyDonation
    list_display = ('user', 'project', 'order')
    raw_id_fields = ('user', 'project', 'order')

admin.site.register(MonthlyDonation, MonthlyDonationAdmin)

