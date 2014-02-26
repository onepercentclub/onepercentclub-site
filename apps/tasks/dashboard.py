from admin_tools.dashboard.modules import DashboardModule
from django.utils.translation import ugettext_lazy as _
from .models import Task


class RecentTasks(DashboardModule):
    """
    """
    title = _('Recently Created Tasks')
    template = 'admin_tools/dashboard/recent_tasks.html'
    limit = 10
    include_list = None
    exclude_list = None

    def __init__(self, title=None, limit=10, **kwargs):
        kwargs.update({'limit': limit})
        super(RecentTasks, self).__init__(title, **kwargs)

    def init_with_context(self, context):
        qs = Task.objects.order_by('-created')

        self.children = qs[:self.limit]
        if not len(self.children):
            self.pre_content = _('No recent projects.')
        self._initialized = True
