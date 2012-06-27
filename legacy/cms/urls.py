from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('cms.views',
    url(r'^overview/', 'overview'),
    url(r'^view/(?P<id>.+)/$', 'view'),
)

