from fluent_dashboard.dashboard import FluentIndexDashboard
from apps.projects.dashboard import SubmittedPlans, FundedProjects, StartedCampaigns
from apps.tasks.dashboard import RecentTasks
from admin_tools_stats.modules import DashboardCharts, get_active_graph, DashboardChart


class CustomIndexDashboard(FluentIndexDashboard):
    """
    Custom Dashboard for onepercentclub-site.
    """
    columns = 3

    def init_with_context(self, context):
        self.children.append(SubmittedPlans())
        self.children.append(StartedCampaigns())
        self.children.append(FundedProjects())
        self.children.append(RecentTasks())

        graph_list = get_active_graph()
        for i in graph_list:
            kwargs = {}
            kwargs['require_chart_jscss'] = True
            kwargs['graph_key'] = i.graph_key

            if context['request'].POST.get('select_box_' + i.graph_key):
                kwargs['select_box_' + i.graph_key] = context['request'].POST['select_box_' + i.graph_key]

            self.children.append(DashboardCharts(**kwargs))

