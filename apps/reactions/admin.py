from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Reaction


class ReactionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_pk'),
        }),
        (_('Content'), {
            'fields': ('author', 'editor', 'reaction'),
        }),
        (_('Metadata'), {
            'fields': ('deleted', 'ip_address'),
        }),
    )

    list_display = ('author_full_name', 'content_type', 'object_pk', 'ip_address', 'created', 'updated', 'deleted')
    list_filter = ('created', 'updated', 'deleted')
    date_hierarchy = 'created'
    ordering = ('-created',)
    raw_id_fields = ('author', 'editor')
    search_fields = ('reaction', 'author__username', 'author__email', 'author__first_name', 'author__last_name', 'ip_address')

    def author_full_name(self, obj):
        full_name = obj.author.get_full_name()
        if not full_name:
            return obj.author.username
        else:
            return full_name
    author_full_name.short_description = _('Author')

admin.site.register(Reaction, ReactionAdmin)
