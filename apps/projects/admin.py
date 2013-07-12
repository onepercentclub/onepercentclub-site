import logging
from apps.projects.models import ProjectPlan, ProjectCampaign, ProjectTheme
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect

logger = logging.getLogger(__name__)

from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin

from .models import (Project, ProjectBudgetLine, PartnerOrganization, ProjectPitch)


class ProjectPitchAdmin(admin.ModelAdmin):

    model = ProjectPitch

    search_fields = ('title',)
    list_filter = ('status', )
    list_display = ('title', 'status', 'created')

    readonly_fields = ('edit_project', 'project')

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPitchAdmin, self).response_change(request, obj)

admin.site.register(ProjectPitch, ProjectPitchAdmin)


class ProjectBudgetInline(admin.TabularInline):
    
    model = ProjectBudgetLine
    extra = 0
    

class ProjectPlanAdmin(admin.ModelAdmin):

    model = ProjectPlan

    search_fields = ('title', )
    list_filter = ('status', )
    list_display = ('title', 'status', 'created')

    readonly_fields = ('edit_project', 'project')

    inlines = (ProjectBudgetInline, )

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPlanAdmin, self).response_change(request, obj)

admin.site.register(ProjectPlan, ProjectPlanAdmin)


class ProjectCampaignAdmin(admin.ModelAdmin):

    model = ProjectCampaign
    list_filter = ('status', )
    list_display = ('project', 'status', 'created')

    readonly_fields = ('edit_project', )
    fields = readonly_fields + ('status', 'deadline', 'money_asked', 'currency')

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPitchAdmin, self).response_change(request, obj)

admin.site.register(ProjectCampaign, ProjectCampaignAdmin)


class ProjectAdmin(AdminImageMixin, admin.ModelAdmin):

    date_hierarchy = 'created'

    save_on_top = True

    prepopulated_fields = {"slug": ("title",)}

    list_filter = ('phase', 'partner_organization')
    list_display = ('title', 'owner', 'coach', 'phase')

    search_fields = ('title', 'owner__first_name', 'owner__last_name')

    raw_id_fields = ('owner', 'coach')

    readonly_fields = ('pitch_view', 'plan_view', 'campaign_view')

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

    def campaign_view(self, obj):
        object = obj.projectcampaign
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name),  args=[object.id] )
        return "<a href='%s'>View/Edit Campaign</a>" % str(url)

    campaign_view.allow_tags = True


admin.site.register(Project, ProjectAdmin)


class PartnerOrganizationAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)


class ProjectThemeAdmin(admin.ModelAdmin):

    model = ProjectTheme

admin.site.register(ProjectTheme, ProjectThemeAdmin)