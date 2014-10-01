from apps.projects.views import ManageProjectBudgetLineDetail, ManageProjectBudgetLineList
from django.conf.urls import patterns, url
from surlex.dj import surl


urlpatterns = patterns('',
    url(r'^budgetlines/$', ManageProjectBudgetLineList.as_view(), name='project-budgetline-list'),
    surl(r'^budgetlines/<pk:#>$', ManageProjectBudgetLineDetail.as_view(), name='project-budgetline-detail'),
)
