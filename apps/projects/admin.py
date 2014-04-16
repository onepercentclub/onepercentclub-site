from apps.projects.models import ProjectBudgetLine, Project
from bluebottle.bb_projects.admin import BaseProjectAdmin
from bluebottle.bb_projects.models import ProjectPhase
from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
import logging

from .models import PartnerOrganization
# from projects.models import OnePercentProject

logger = logging.getLogger(__name__)


class PartnerOrganizationAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)


class ProjectBudgetLineInline(admin.TabularInline):
    model = ProjectBudgetLine
    extra = 0


class ProjectAdmin(BaseProjectAdmin):
    inlines = (ProjectBudgetLineInline, )


admin.site.register(Project, ProjectAdmin)