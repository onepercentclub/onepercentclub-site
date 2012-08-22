import logging
logger = logging.getLogger(__name__)

from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail.shortcuts import get_thumbnail

from .models import (
    Project, IdeaPhase, FundPhase, ActPhase, ResultsPhase, BudgetLine,
    Testimonial, Message, ProjectTheme
)


class IdeaPhaseInline(admin.StackedInline):
    model = IdeaPhase
    can_delete = False


class BudgetInline(admin.TabularInline):
    model = BudgetLine


class FundPhaseInline(admin.StackedInline):
    model = FundPhase


class ActPhaseInline(admin.StackedInline):
    model = ActPhase


class ResultsPhaseInline(admin.StackedInline):
    model = ResultsPhase


class ProjectAdmin(AdminImageMixin, admin.ModelAdmin):
    date_hierarchy = 'created'

    prepopulated_fields = {"slug": ("title",)}

    list_filter = ('phase', 'project_language', 'themes', 'country')
    list_display = ('title', 'organization', 'country')
    
    inlines = [
        BudgetInline, IdeaPhaseInline,
        FundPhaseInline, ActPhaseInline, ResultsPhaseInline
    ]

    filter_horizontal = ('themes', 'albums')

    search_fields = (
        'title', 'organization__title',
        'owner__first_name', 'owner__last_name'
    )

admin.site.register(Project, ProjectAdmin)
admin.site.register(Message)
admin.site.register(Testimonial)



class ProjectThemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(ProjectTheme, ProjectThemeAdmin)
