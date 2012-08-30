from django.conf.urls.defaults import patterns, url, include

from surlex.dj import surl

from .api import ProjectPreviewResource, ProjectDetailResource, ProjectSearchFormResource

projectpreview_resource = ProjectPreviewResource()
projectdetail_resource = ProjectDetailResource()
projectsearchform_resource = ProjectSearchFormResource()

urlpatterns = patterns('',
    url(r'^', include(projectpreview_resource.urls)),
    url(r'^', include(projectdetail_resource.urls)),
    url(r'^', include(projectsearchform_resource.urls)),
)

