import logging
logger = logging.getLogger(__name__)

from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail.shortcuts import get_thumbnail

from .models import (
    Project, IdeaPhase, PlanPhase, ActPhase, ResultsPhase, BudgetLine,
    Testimonial, BudgetCategory, Message, ProjectCategory
)


class IdeaPhaseInline(admin.StackedInline):
    model = IdeaPhase
    can_delete = False


class BudgetInline(admin.TabularInline):
    model = BudgetLine


class PlanPhaseInline(admin.StackedInline):
    model = PlanPhase


class ActPhaseInline(admin.StackedInline):
    model = ActPhase


class ResultsPhaseInline(admin.StackedInline):
    model = ResultsPhase


class ProjectAdmin(AdminImageMixin, admin.ModelAdmin):
    date_hierarchy = 'created'

    prepopulated_fields = {"slug": ("title",)}

    list_filter = ('phase', 'project_language', 'categories', 'country')
    list_display = ('thumbnail', 'title', 'organization', 'country')
    list_display_links = ('thumbnail', 'title')

    inlines = [
        BudgetInline, IdeaPhaseInline,
        PlanPhaseInline, ActPhaseInline, ResultsPhaseInline
    ]

    filter_horizontal = ('categories', 'albums')

    search_fields = (
        'title', 'organization__title',
        'owner__first_name', 'owner__last_name'
    )

    def thumbnail(self, instance):
        """
        Generate a nice little thumbnail for our project.

        Source: https://github.com/sorl/sorl-thumbnail/blob/master/sorl/thumbnail/admin/current.py#L19
        """
        value = '<div style="height:80px;width:80px">%s</div>'

        if instance.image:
            try:
                mini = get_thumbnail(
                    instance.image, '80x80', upscale=False, crop='center'
                )
            except Exception:
                logger.exception('An error occurred while scaling an image in the admin.')
                return value % ''
            else:
                # We might need this later, for explicitly linking and/or
                # formatting of the image and/or link.
                #
                # output = (
                #     u'<div style="float:left">'
                #     u'<a style="width:%spx;display:block;margin:0 0 10px" class="thumbnail" target="_blank" href="%s">'
                #     u'<img src="%s"></a>%s</div>'
                #     ) % (mini.width, value.url, mini.url, output)
                return value % (u'<img width="%s" height="%s" src="%s">' \
                    % (mini.width, mini.height, mini.url))
        else:
            return value % ''
    thumbnail.allow_tags = True

admin.site.register(Project, ProjectAdmin)
admin.site.register(Message)
admin.site.register(Testimonial)
admin.site.register(BudgetCategory)


class ProjectCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(ProjectCategory, ProjectCategoryAdmin)
