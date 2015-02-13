from django.conf.urls import patterns
from surlex.dj import surl
from .views import AccountingOverviewView

urlpatterns = patterns('',
    surl(r'^overview/$', AccountingOverviewView.as_view(), name='admin-accounting-overview'),
)
