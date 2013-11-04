from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Sum
from django.http.response import HttpResponseRedirect
from django.utils import formats, translation
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _


from babel.numbers import format_currency
from sorl.thumbnail.admin import AdminImageMixin
import logging


from .models import (Project, ProjectBudgetLine, PartnerOrganization, 
                     ProjectPitch, ProjectPlan, ProjectCampaign,
                     ProjectTheme, ProjectPhases, ProjectResult, ProjectPhaseLog)


logger = logging.getLogger(__name__)


class ProjectPitchAdmin(admin.ModelAdmin):
    model = ProjectPitch

    search_fields = ('title',)
    list_filter = ('status',)
    list_display = ('title', 'status', 'created')
    readonly_fields = ('edit_project', 'project', 'project_owner')

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPitchAdmin, self).response_change(request, obj)


admin.site.register(ProjectPitch, ProjectPitchAdmin)


class ProjectBudgetInline(admin.TabularInline):
    model = ProjectBudgetLine
    extra = 0
    fields = ('description', 'amount_override', 'amount', 'currency')
    readonly_fields = ('amount_override',)
    verbose_name_plural = _("Budget")

    def amount_override(self, obj):
        language = translation.get_language().split('-')[0]
        return format_currency(obj.amount / 100.0, obj.currency, locale=language)

    amount_override.short_description = 'amount'

    class Media:
        css = {"all": ("css/admin/hide_admin_original.css",)}


class ProjectPlanAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('status',)
    list_display = ('title', 'status', 'created')
    fields = ('edit_project', 'project_owner', 'project_organization', 'status', 'title', 'pitch', 'need', 'theme',
              'description', 'effects', 'for_who', 'future', 'reach', 'latitude', 'longitude', 'country', 'image',
              'video_url', 'money_needed', 'campaign', 'tags', 'budget_total')
    readonly_fields = ('edit_project', 'project_owner', 'project_organization', 'budget_total')
    inlines = (ProjectBudgetInline,)

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def project_organization(self, obj):
        object = obj.organization
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.name)

    project_organization.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectPlanAdmin, self).response_change(request, obj)

    def budget_total(self, obj):
            budget_lines = obj.projectbudgetline_set
            language = translation.get_language().split('-')[0]
            if budget_lines.count() > 0:
                # Assumes all budget lines use the same currency.
                currency = budget_lines.all()[0].currency
                budget_total = budget_lines.aggregate(Sum('amount'))['amount__sum']
                return format_currency(budget_total / 100.0, currency, locale=language)
            else:
                return format_currency(0, 'EUR', locale=language)


admin.site.register(ProjectPlan, ProjectPlanAdmin)


class ProjectCampaignAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('project', 'status', 'created')

    readonly_fields = ('edit_project', 'project_owner')
    fields = readonly_fields + ('status', 'deadline', 'money_asked', 'currency')

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectCampaignAdmin, self).response_change(request, obj)


admin.site.register(ProjectCampaign, ProjectCampaignAdmin)


class ProjectResultAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('project', 'status', 'created')

    readonly_fields = ('edit_project', 'project_owner')
    fields = readonly_fields + ('status',)

    def edit_project(self, obj):
        object = obj.project
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.title)

    edit_project.allow_tags = True

    def project_owner(self, obj):
        object = obj.project.owner
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            object = obj.project
            url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
            return HttpResponseRedirect(url)
        else:
            return super(ProjectResultAdmin, self).response_change(request, obj)


admin.site.register(ProjectResult, ProjectResultAdmin)


class ProjectAdmin(AdminImageMixin, admin.ModelAdmin):
    date_hierarchy = 'created'
    ordering = ('-created',)
    save_on_top = True
    actions = ('set_failed',)

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
        return queryset.select_related('projectpitch', 'projectplan', 'projectcampaign', 'owner',
                                       'partner_organization')

    def get_title_display(self, obj):
        if len(obj.title) > 50:
            return u'<span title="{title}">{short_title} [...]</span>'.format(title=escape(obj.title),
                                                                              short_title=obj.title[:45])
        return obj.title

    get_title_display.allow_tags = True
    get_title_display.admin_order_field = 'title'
    get_title_display.short_description = _('title')

    def get_owner_display(self, obj):
        owner_name = obj.owner.get_full_name()
        if owner_name:
            owner_name = u' ({name})'.format(name=owner_name)
        return u'{email}{name}'.format(name=owner_name, email=obj.owner.email)

    get_owner_display.admin_order_field = 'owner__last_name'
    get_owner_display.short_description = _('owner')

    def project_organization(self, obj):
        object = obj.projectplan.organization
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.name)

    project_organization.allow_tags = True

    def funded(self, obj):
        try:
            # 
            funded = obj.projectcampaign.percentage_funded
            if funded == 100.0:
                try:
                    phase_log = obj.projectphaselog_set.get(phase=ProjectPhases.act)
                    created = formats.date_format(phase_log.created, 'SHORT_DATETIME_FORMAT')
                    return u'{funded} % ({date})'.format(funded=funded, date=created)
                except ProjectPhaseLog.DoesNotExist:
                    pass
            return u'{funded} %'.format(funded=funded)
        except ProjectCampaign.DoesNotExist:
            return _('n/a')

    def project_owner(self, obj):
        object = obj.owner
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>%s</a>" % (str(url), object.first_name + ' ' + object.last_name)

    project_owner.allow_tags = True

    def pitch_view(self, obj):
        object = obj.projectpitch
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>View/Edit Pitch</a>" % str(url)

    pitch_view.allow_tags = True

    def plan_view(self, obj):
        object = obj.projectplan
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
        return "<a href='%s'>View/Edit Plan</a>" % str(url)

    plan_view.allow_tags = True

    def campaign_view(self, obj):
        object = obj.projectcampaign
        url = reverse('admin:%s_%s_change' % (object._meta.app_label, object._meta.module_name), args=[object.id])
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

admin.site.register(ProjectTheme)