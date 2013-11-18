from django.conf.urls import patterns, url


from apps.fundraiser.views import FundRaiserListView

urlpatterns = patterns('',
    # TODO: filtering via querystring?
    url(r'^fundraisers/$', FundRaiserListView.as_view(), name='fundraiser-list'),
)