from apps.donations.models import MonthlyDonation, MonthlyBatch, MonthlyOrder
from django.contrib import admin


class MonthlyBatchAdmin(admin.ModelAdmin):
    model = MonthlyBatch
    list_display = ('id', 'date')

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

