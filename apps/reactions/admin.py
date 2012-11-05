from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Reaction


class ReactionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,
         {'fields': ('content_type', 'object_pk', 'site')}
            ),
        (_('Content'),
         {'fields': ('author', 'reaction')}
            ),
        (_('Metadata'),
         {'fields': ('created', 'ip_address', 'deleted')}
            ),
        )

    list_display = ('author_full_name', 'content_type', 'object_pk', 'ip_address', 'created', 'deleted')
    list_filter = ('created', 'site', 'deleted')
    date_hierarchy = 'created'
    ordering = ('-created',)
    raw_id_fields = ('author',)
    search_fields = ('reaction', 'author__username', 'author__email', 'author__last_name', 'author__first_name', 'ip_address')

    def author_full_name(self, obj):
        full_name = obj.author.get_full_name()
        if not full_name:
            return obj.author.username
        else:
            return full_name
    author_full_name.short_description = _('Author')

admin.site.register(Reaction, ReactionAdmin)
