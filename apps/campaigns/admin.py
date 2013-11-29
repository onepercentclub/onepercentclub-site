from django.contrib import admin

from .models import Campaign


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end', 'target')
    list_filter = ('start', 'end')
    readonly_fields = ('created', 'updated', 'deleted',)
    fields = ('title', 'start', 'end', 'target', 'currency') + readonly_fields

    search_fields = ('title',)

admin.site.register(Campaign, CampaignAdmin)