from apps.recurring_donations.views import MonthlyDonationList, MonthlyDonationDetail, MonthlyDonationProjectList, \
    MonthlyDonationProjectDetail
from django.conf.urls import patterns, url


urlpatterns = patterns('',
    # Monthly donations (MonthlyDonor)
    url(r'^$', MonthlyDonationList.as_view(), name='monthly-donation-list'),
    url(r'^(?P<pk>\d+)', MonthlyDonationDetail.as_view(), name='monthly-donation-detail'),

    # Monthly donation projects (MonthlyDonorProject)
    url(r'^projects/$', MonthlyDonationProjectList.as_view(), name='monthly-donation-project-list'),
    url(r'^projects/(?P<pk>\d+)', MonthlyDonationProjectDetail.as_view(), name='monthly-donation-project-detail')

)
