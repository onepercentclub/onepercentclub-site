from django.contrib import admin
from django.utils import translation

from babel.numbers import format_currency

from .models import FundRaiser

class FundRaiserAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount_override', 'deadline', 'amount_donated_override')

    raw_id_fields = ('project', 'owner')

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

    def amount_donated_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(int(obj.amount) / 100.0, obj.currency, locale=language)

    amount_donated_override.short_description = 'amount donated'

admin.site.register(FundRaiser, FundRaiserAdmin)