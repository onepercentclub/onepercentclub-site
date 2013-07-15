
from django.contrib import admin
from django.contrib.redirects.models import Redirect

from .actions import export_as_csv_action

FIELD_LIST = ('old_path', 'new_path', 'regular_expression', 'fallback_redirect', 'nr_times_visited')

class RedirectAdmin(admin.ModelAdmin):
    list_display = FIELD_LIST
    list_filter = ('regular_expression',)
    search_fields = ('old_path', 'new_path')

    actions = [export_as_csv_action('Export to CSV', fields=FIELD_LIST)]

admin.site.register(Redirect, RedirectAdmin)
