from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('projects.views',
    url(r'^overview/', 'overview'),
    url(r'^view/(?P<name>.+)/$', 'view'),
)

