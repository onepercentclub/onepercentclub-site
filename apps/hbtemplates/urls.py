from django.conf import settings
from django.conf.urls import patterns, url
from .views import HBTemplateView

# Create a regex pattern for all installed bluebottle apps.
apps_prefix = 'apps.'
apps_regex = ''
for installed_app in settings.INSTALLED_APPS:
    if installed_app.startswith(apps_prefix):
        apps_regex += installed_app[len(apps_prefix):] + '|'
apps_regex = apps_regex[:-1]

urlpatterns = patterns('',
    # The hb templates can be placed as follows in any bluebottle app:
    #   'templates/<app-name>/<template-name>.hb.html'
    url(r'(?P<app>(%s))/(?P<hbtemplate>\w+\.hb\.html)$' % apps_regex, HBTemplateView.as_view()),
)