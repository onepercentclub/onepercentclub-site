from django.conf import settings
from django.contrib import admin
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from .models import Quote


class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote', 'status_column', 'modification_date', 'language', 'segment')
    list_filter = ('status', 'language', 'segment')
    date_hierarchy = 'publication_date'
    search_fields = ('quote', )
    model = Quote

    raw_id_fields = ('user', )

    fieldsets = (
        (None, {
            'fields': ('quote', 'segment', 'language', 'user'),
        }),
        (_('Publication settings'), {
            'fields': ('status', 'publication_date', 'publication_end_date'),
        }),
    )

    radio_fields = {
        'status': admin.HORIZONTAL,
        'language': admin.HORIZONTAL,
    }

    STATUS_ICONS = {
        Quote.QuoteStatus.published: 'icon-yes.gif',
        Quote.QuoteStatus.draft: 'icon-unknown.gif',
    }

    def status_column(self, quote):
        status = quote.status
        title = [rec[1] for rec in quote.QuoteStatus.choices if rec[0] == status].pop()
        icon  = self.STATUS_ICONS[status]
        admin = settings.STATIC_URL + 'admin/img/'
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(admin=admin, icon=icon, title=title)

    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user

        if not obj.publication_date:
            # auto_now_add makes the field uneditable.
            # default fills the field before the post is written (too early)
            obj.publication_date = now()
        obj.save()

    status_column.allow_tags = True
    status_column.short_description = _('Status')

admin.site.register(Quote, QuoteAdmin)
