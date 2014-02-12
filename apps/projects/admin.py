from bluebottle.bb_projects.admin import BaseProjectAdmin
from bluebottle.bb_projects.models import ProjectPhase
from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
import logging

from .models import PartnerOrganization
# from projects.models import OnePercentProject

logger = logging.getLogger(__name__)


# class OnePercentProjectAdmin(BaseProjectAdmin):
#
#     raw_id_fields = ('owner', 'organization', 'coach')
#
# admin.site.register(OnePercentProject, OnePercentProjectAdmin)

class PartnerOrganizationAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)

# admin.site.register(ProjectPhase)
