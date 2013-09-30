import logging
from apps.projects.models import ProjectPlan, ProjectCampaign, ProjectTheme, ProjectPhases, ProjectResult
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)

from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin

from .models import (Project, ProjectBudgetLine, PartnerOrganization, ProjectPitch)


class ProjectPitchAdmin(admin.ModelAdmin):

    model = ProjectPitch

    search_fields = ('title',)
    list_filter = ('status', )
    list_display = ('title', 'status', 'created')
    readonly_fields = ('edit_project', 'project', 'project_owner')

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True


    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
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

    readonly_fields = ('edit_project', 'project_owner', 'project_organization')

    fields = readonly_fields + ('status', 'title', 'pitch', 'need', 'theme', 'description', 'effects', 'for_who',
                                'future', 'reach', 'latitude', 'longitude', 'country', 'image', 'video_url',
                                'money_needed', 'campaign', 'tags')

    inlines = (ProjectBudgetInline, )

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def project_organization(self, obj):
        object = obj.organization
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.name)

    project_organization.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPlanAdmin, self).response_change(request, obj)

admin.site.register(ProjectPlan, ProjectPlanAdmin)


class ProjectCampaignAdmin(admin.ModelAdmin):

    model = ProjectCampaign
    list_filter = ('status', )
    list_display = ('project', 'status', 'created')

    readonly_fields = ('edit_project', 'project_owner')
    fields = readonly_fields + ('status', 'deadline', 'money_asked', 'currency')

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPitchAdmin, self).response_change(request, obj)

admin.site.register(ProjectCampaign, ProjectCampaignAdmin)


class ProjectResultAdmin(admin.ModelAdmin):

    model = ProjectResult
    list_filter = ('status', )
    list_display = ('project', 'status', 'created')

    readonly_fields = ('edit_project', 'project_owner')
    fields = readonly_fields + ('status', )

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectResultAdmin, self).response_change(request, obj)

admin.site.register(ProjectResult, ProjectResultAdmin)


class ProjectAdmin(AdminImageMixin, admin.ModelAdmin):

    date_hierarchy = 'created'
    ordering = ('-created',)
    save_on_top = True
    actions = ('set_failed', )

    prepopulated_fields = {"slug": ("title",)}

    list_filter = ('phase', 'partner_organization')
    list_display = ('get_title_display', 'get_owner_display', 'coach', 'phase', 'funded', 'created')

    search_fields = ('title', 'owner__first_name', 'owner__last_name', 'partner_organization__name')

    raw_id_fields = ('owner', 'coach')

    readonly_fields = ('project_owner', 'pitch_view', 'plan_view', 'campaign_view', 'funded')

    fields = readonly_fields + ('owner', 'coach', 'title', 'slug', 'phase', 'partner_organization')

    def queryset(self, request):
        # Optimization: Select related fields that are used in admin specific display fields.
        queryset = super(ProjectAdmin, self).queryset(request)
        return queryset.select_related('projectpitch', 'projectplan', 'projectcampaign', 'owner', 'partner_organization')

    def get_title_display(self, obj):
        if len(obj.title) > 50:
            return u'<span title="{title}">{short_title} [...]</span>'.format(title=escape(obj.title), short_title=obj.title[:45])
        return obj.title
    get_title_display.allow_tags = True
    get_title_display.admin_order_field  = 'title'
    get_title_display.short_description = _('title')

    def get_owner_display(self, obj):
        owner_name = obj.owner.get_full_name()
        if owner_name:
            owner_name = u' ({name})'.format(name=owner_name)
        return u'{email}{name}'.format(name=owner_name, email=obj.owner.email)
    get_owner_display.admin_order_field  = 'owner__last_name'
    get_owner_display.short_description = _('owner')

    def funded(self, obj):
        try:
            return u'{funded} %'.format(funded=obj.projectcampaign.percentage_funded)
        except ProjectCampaign.DoesNotExist:
            return _('n/a')

    def project_owner(self, obj):
        object = obj.owner
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def pitch_view(self, obj):
        object = obj.projectpitch
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>View/Edit Pitch</a>" % str(url)

    pitch_view.allow_tags = True

    def plan_view(self, obj):
        object = obj.projectplan
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>View/Edit Plan</a>" % str(url)

    plan_view.allow_tags = True

    def campaign_view(self, obj):
        object = obj.projectcampaign
        url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.module_name), args=[object.id])
        return "<a href='%s'>View/Edit Campaign</a>" % str(url)

    campaign_view.allow_tags = True

    def set_failed(self, request, queryset):
        rows_updated = queryset.update(phase=ProjectPhases.failed)

        if rows_updated == 1:
            message = "one project was marked as failed."
        else:
            message = "{0} projects were marked as failed.".format(rows_updated)
        self.message_user(request, message)


    set_failed.short_description = _("Mark selected projects as failed")

admin.site.register(Project, ProjectAdmin)


class PartnerOrganizationAdmin(AdminImageMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)


class ProjectThemeAdmin(admin.ModelAdmin):

    model = ProjectTheme

admin.site.register(ProjectTheme, ProjectThemeAdmin)