from django.utils.translation import ugettext as _
from django.contrib import admin

from .models import GroupPage, GroupPageSlide


class GroupPageSlideInline(admin.StackedInline):
    model = GroupPageSlide
    extra = 0
    verbose_name_plural = _("Slides")


class GroupPageAdmin(admin.ModelAdmin):
    model = GroupPage
    raw_id_fields = ('owner', 'members', 'projects')

    inlines = (GroupPageSlideInline, )


admin.site.register(GroupPage, GroupPageAdmin)
