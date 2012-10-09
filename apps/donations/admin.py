from django.contrib import admin

from .models import Donation


class DonationAdmin(admin.ModelAdmin):
    model = Donation

    date_hierarchy = 'created'

    list_display = ('created', 'user', 'amount')
    list_filter = ('status', )

    search_fields = (
        'user__first_name', 'user__last_name', 'project__title'
    )


admin.site.register(Donation, DonationAdmin)