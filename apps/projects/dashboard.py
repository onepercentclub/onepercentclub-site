from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


from admin_tools.dashboard.modules import DashboardModule
from apps.projects.models import (Project, ProjectPitch, ProjectPlan, 
                                  ProjectResult, ProjectCampaign, ProjectPhases)


class RecentProjects(DashboardModule):
    title = _('Recently Created Projects')
    template = 'admin_tools/dashboard/recent_projects.html'
    limit = 10

    def __init__(self, title=None, limit=10, **kwargs):
        kwargs.update({'limit': limit})
        super(RecentProjects, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        qs = Project.objects.order_by('-created')
        self.children = qs[:self.limit]
        if not len(self.children):
            self.pre_content = _('No recent projects.')
        self._initialized = True


class SubmittedPitches(DashboardModule):
    title = _('Recently Submitted Pitches')
    template = 'admin_tools/dashboard/submitted_pitches.html'
    limit = 10

    def __init__(self, title=None, limit=10, **kwargs):
        kwargs.update({'limit': limit})
        super(SubmittedPitches, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        qs = ProjectPitch.objects.order_by('created')
        qs = qs.filter(status=ProjectPitch.PitchStatuses.submitted)
        self.children = qs[:self.limit]
        if not len(self.children):
            self.pre_content = _('No submitted pitches.')
        self._initialized = True


class SubmittedPlans(DashboardModule):
    title = _('Recently Submitted Plans')
    template = 'admin_tools/dashboard/submitted_plans.html'
    limit = 10

    def __init__(self, title=None, limit=10,**kwargs):
        kwargs.update({'limit': limit})
        super(SubmittedPlans, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        qs = ProjectPlan.objects.order_by('created')
        qs = qs.filter(status=ProjectPlan.PlanStatuses.submitted)

        self.children = qs[:self.limit]
        if not len(self.children):
            self.pre_content = _('No submitted plans.')
        self._initialized = True


class StartedCampaigns(DashboardModule):
    title = _('Recently Started Campaigns')
    template = 'admin_tools/dashboard/started_campaigns.html'
    limit = 10

    def __init__(self, title=None, limit=10,**kwargs):
        kwargs.update({'limit': limit})
        super(StartedCampaigns, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        qs = ProjectCampaign.objects.order_by('-created')
        qs = qs.filter(status=ProjectCampaign.CampaignStatuses.running)

        self.children = qs[:self.limit]
        if not len(self.children):
            self.pre_content = _('No campaigns.')
        self._initialized = True


class FundedProjects(DashboardModule):
    title = _('Recently Funded Projects')
    template = 'admin_tools/dashboard/recent_funded_projects.html'
    limit = 10

    def __init__(self, title=None, limit=10, **kwargs):
        kwargs.update({'limit': limit})
        super(FundedProjects, self).__init__(title, **kwargs)

    def init_with_context(self, context):

        qs1 = Project.objects.filter(
                Q(projectphaselog__phase=ProjectPhases.act)
            ).order_by('-projectphaselog__created')[:self.limit]

        qs1_project_ids = qs1.values_list('id', flat=True)
        qs2 = Project.objects.filter(
                projectresult__status = ProjectResult.ResultStatuses.running
            ).exclude(
                projectresult = None
            ).exclude(
                id__in = qs1_project_ids
            ).order_by('-projectresult__created')[:self.limit]

        projects = list(qs1) + list(qs2)

        # sort the projects based on act phase reached or projectresult created
        sorted(projects, key=lambda project: project.date_funded, reverse=True)
        
        self.children = projects[:self.limit]
        if not len(self.children):
            self.pre_content = _('No recently funded projects.')
        self._initialized = True

