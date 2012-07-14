from django.conf.urls.defaults import patterns, url, include
from .api import ProjectResource, IdeaPhaseResource

project_resource = ProjectResource()
ideaphase_resource = IdeaPhaseResource()


urlpatterns = patterns('apps.projects.views',
    url(r'^test/', 'test'),
#    url(r'^overview/', 'overview'),
#    url(r'^view/(?P<name>.+)/$', 'view'),
)

# API urls
urlpatterns += patterns('',
    url(r'^api/', include(project_resource.urls)),
    url(r'^api/', include(ideaphase_resource.urls)),
)

