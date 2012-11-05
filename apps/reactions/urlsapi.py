from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from surlex.dj import surl
from .views import ReactionRoot, ReactionInstance

urlpatterns = patterns('',
    url(r'^$', ReactionRoot.as_view(), name='reaction-root'),
    surl(r'^<slug:s>$', ReactionInstance.as_view(), name='reaction-instance'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
