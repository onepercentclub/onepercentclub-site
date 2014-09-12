from decimal import Decimal
from apps.projects.models import ProjectBudgetLine, Project
from bluebottle.bb_projects.admin import BaseProjectAdmin
from bluebottle.utils.admin import export_as_csv_action
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.core.urlresolvers import reverse
from sorl.thumbnail.admin import AdminImageMixin
import logging

from .models import PartnerOrganization

logger = logging.getLogger(__name__)


class PartnerOrganizationAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)


class ProjectBudgetLineInline(admin.TabularInline):
    model = ProjectBudgetLine
    extra = 0


class ProjectAdmin(BaseProjectAdmin):
    inlines = (ProjectBudgetLineInline, )

    list_filter = BaseProjectAdmin.list_filter + ('is_campaign', 'theme', 'partner_organization')
    list_display = BaseProjectAdmin.list_display + ('is_campaign', 'deadline', 'donated_percentage')
    list_editable = ('is_campaign', )

    readonly_fields = ('owner_link', 'organization_link', 'amount_donated', 'amount_needed', 'popularity')

    export_fields = ['title', 'owner', 'created', 'status', 'deadline', 'amount_asked', 'amount_donated']
    actions = (export_as_csv_action(fields=export_fields), )

    def owner_link(self, obj):
        object = obj.owner
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    owner_link.allow_tags = True

    def organization_link(self, obj):
        object = obj.organization
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.name)

    organization_link.allow_tags = True

    def donated_percentage(self, obj):
        if not obj.amount_asked:
            return "-"
        percentage = "%.2f" % (100 * obj.amount_donated / obj.amount_asked)
        return "{0} %".format(percentage)




# We wrapped this in a try because sometimes Project hasn't got registered before it hits this.
try:
    admin.site.unregister(Project)
except NotRegistered:
    pass
admin.site.register(Project, ProjectAdmin)
