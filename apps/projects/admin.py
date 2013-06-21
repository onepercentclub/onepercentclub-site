import logging
from apps.fund.models import Donation
from apps.projects.models import ProjectPlan
from django.contrib.admin.filters import FieldListFilter
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail.shortcuts import get_thumbnail

from .models import (Project, ProjectBudgetLine, PartnerOrganization, ProjectPitch)


class ProjectPitchAdmin(admin.ModelAdmin):

    model = ProjectPitch

    list_filter = ('status', )
    list_display = ('title', 'status', 'created')
    raw_id_fields = ('project', )

admin.site.register(ProjectPitch, ProjectPitchAdmin)


class ProjectPlanAdmin(admin.ModelAdmin):

    model = ProjectPlan

    list_filter = ('status', )
    list_display = ('title', 'status', 'created')
    raw_id_fields = ('project', )

admin.site.register(ProjectPlan, ProjectPlanAdmin)


class ProjectAdmin(AdminImageMixin, admin.ModelAdmin):

    date_hierarchy = 'created'

    save_on_top = True

    prepopulated_fields = {"slug": ("title",)}

    list_filter = ('phase', 'partner_organization')
    list_display = ('title', 'owner', 'coach', 'phase')

    search_fields = ('title', 'owner__first_name', 'owner__last_name')

    raw_id_fields = ('owner', 'coach')

    readonly_fields = ('pitch_view', 'plan_view')

    fields = readonly_fields + ('owner', 'coach', 'title', 'slug', 'phase', 'partner_organization')

    def pitch_view(self, obj):
        object = obj.projectpitch
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
        return "<a href='%s'>View/Edit Pitch</a>" % str(url)

    pitch_view.allow_tags = True

    def plan_view(self, obj):
        object = obj.projectplan
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
        return "<a href='%s'>View/Edit Plan</a>" % str(url)

    plan_view.allow_tags = True


admin.site.register(Project, ProjectAdmin)


class PartnerOrganizationAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)


