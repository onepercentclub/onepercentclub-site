from django.contrib import admin

from .models import Donation, DonationLine


class DonationLineInline(admin.StackedInline):
    model = DonationLine
    max_num = 0
    can_delete = False


class DonationAdmin(admin.ModelAdmin):
    model = Donation

    inlines = [DonationLineInline, ]

    date_hierarchy = 'created'

    list_display = ('created', 'user', 'amount')
    list_filter = ('status', )

    search_fields = (
        'user__first_name', 'user__last_name', 'donationline__project__title'
    )


admin.site.register(Donation, DonationAdmin)