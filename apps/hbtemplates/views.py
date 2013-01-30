import os
import sys
from django import http
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.views.generic.base import TemplateView


# The code to create bb_app_template_dirs is from Django templates app loader.
# https://github.com/django/django/blob/e86e4ce0bd0a538fcde0f9b0c4f26c6810621bb5/django/template/loaders/app_directories.py#L16

# At compile time, cache the directories to search.
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_template_dirs = []
for app in settings.INSTALLED_APPS:
    if not app.startswith('apps.'):
        continue
    try:
        mod = import_module(app)
    except ImportError, e:
        raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir.decode(fs_encoding))

# It won't change, so convert it to a tuple to save memory.
bb_app_template_dirs = tuple(app_template_dirs)


class HBTemplateView(TemplateView):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        if kwargs.has_key('hbtemplate'):
            hbtemplate = kwargs.get('hbtemplate')
            if not self._check_template_exists(hbtemplate):
                raise http.Http404
            self.template_name = os.path.join(hbtemplate)
            return super(HBTemplateView, self).get(request, *args, **kwargs)
        else:
            raise http.Http404

    def _check_template_exists(self, hbtemplate):
        for template_dir in bb_app_template_dirs:
            if template_dir.endswith('templates'):
                if os.path.isfile(os.path.join(template_dir, hbtemplate)):
                    return True
        return False
