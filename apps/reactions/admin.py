from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Reaction


class ReactionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,
         {'fields': ('content_type', 'object_pk')}
            ),
        (_('Content'),
         {'fields': ('owner', 'editor', 'reaction')}
            ),
        (_('Metadata'),
         {'fields': ('deleted', 'ip_address')}
            ),
        )

    list_display = ('owner_full_name', 'content_type', 'object_pk', 'ip_address', 'created', 'updated', 'deleted')
    list_filter = ('created', 'updated', 'deleted')
    date_hierarchy = 'updated'
    ordering = ('-updated',)
    raw_id_fields = ('owner', 'editor')
    search_fields = ('reaction', 'author__username', 'author__email', 'author__first_name', 'author__last_name', 'ip_address')

    def owner_full_name(self, obj):
        full_name = obj.owner.get_full_name()
        if not full_name:
            return obj.owner.username
        else:
            return full_name
    owner_full_name.short_description = _('Author')

admin.site.register(Reaction, ReactionAdmin)
