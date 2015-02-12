from admin_tools.dashboard import modules
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from fluent_dashboard.dashboard import FluentIndexDashboard
from apps.projects.dashboard import SubmittedPlans, EndedProjects, StartedCampaigns
from apps.tasks.dashboard import RecentTasks


class CustomIndexDashboard(FluentIndexDashboard):
    """
    Custom Dashboard for onepercentclub-site.
    """
    columns = 3

    def init_with_context(self, context):
        self.children.append(SubmittedPlans())
        self.children.append(StartedCampaigns())
        self.children.append(EndedProjects())
        self.children.append(RecentTasks())

        self.children.append(modules.LinkList(_('Shortcuts'), children=[
            {
                'title': _('Accountancy overview'),
                'url': reverse('admin-accounting-overview'),
                'external': False
            },
        ]))
