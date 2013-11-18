from django.contrib import admin

from .models import FundRaiser

class FundRaiserAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'deadline')

    raw_id_fields = ('project', 'owner')


admin.site.register(FundRaiser, FundRaiserAdmin)