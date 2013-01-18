from django.conf.urls import patterns, url
from .views import HBTemplateView

urlpatterns = patterns('',
    # The hb templates can be placed as follows in any bluebottle app:
    #   'templates/<template-name>.hb.html'
    url(r'(?P<hbtemplate>\w+\.hbs)$', HBTemplateView.as_view()),
)