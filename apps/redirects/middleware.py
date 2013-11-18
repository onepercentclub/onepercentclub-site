from __future__ import unicode_literals

import urllib
import re

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django import http
from django.utils import translation

from apps.redirects.models import Redirect


class RedirectFallbackMiddleware(object):
    """
    A modified version of django.contrib.redirects, this app allows
    us to optionally redirect users using regular expressions.

    It is based on: http://djangosnippets.org/snippets/2784/
    """
    def __init__(self):
        if 'django.contrib.sites' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured(
                "You cannot use RedirectFallbackMiddleware when "
                "django.contrib.sites is not installed."
            )

    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a redirect for non-404 responses.

        full_path = request.get_full_path()
        current_site = get_current_site(request)
        http_host = request.META.get('HTTP_HOST', '')
        if http_host:
            # Crappy workaround for localhost.
            # Always default to https if not on local machine. This will hopefully fix Safari problems.
            if current_site in ['localhost', 'localhost:8000', '127.0.0.1:8000', '127.0.0.1']:
                http_host = 'http://' + http_host
            else:
                http_host = 'https://' + http_host

        language = translation.get_language()

        redirects = Redirect.objects.all().order_by('fallback_redirect')
        for redirect in redirects:
            # Attempt a regular match
            if redirect.old_path == full_path:
                redirect.nr_times_visited += 1
                redirect.save()
                return http.HttpResponsePermanentRedirect(http_host + '/' + language + redirect.new_path)

            if settings.APPEND_SLASH and not request.path.endswith('/'):
                # Try appending a trailing slash.
                path_len = len(request.path)
                slashed_full_path = full_path[:path_len] + '/' + full_path[path_len:]

                if redirect.old_path == slashed_full_path:
                    redirect.nr_times_visited += 1
                    redirect.save()
                    return http.HttpResponsePermanentRedirect(http_host + '/' + language + redirect.new_path)

        # Attempt all regular expression redirects
        reg_redirects = Redirect.objects.filter(regular_expression=True).order_by('fallback_redirect')
        for redirect in reg_redirects:
            try:
                old_path = re.compile(redirect.old_path, re.IGNORECASE)
            except re.error:
                # old_path does not compile into regex, ignore it and move on to the next one
                continue
                
            if re.match(redirect.old_path, full_path):
                # Convert $1 into \1 (otherwise users would have to enter \1 via the admin 
                # which would have to be escaped)
                new_path = redirect.new_path.replace('$', '\\')
                replaced_path = re.sub(old_path, new_path, full_path)
                redirect.nr_times_visited += 1
                redirect.save()
                return http.HttpResponsePermanentRedirect(http_host + '/' + language + replaced_path)

        # No redirect was found. Return the response.
        return response


class RedirectHashCompatMiddleware(object):
    """
    Compatability middleware to make Safari 6 and Internet Explorer < 10 work with the hash after a redirect.
    """
    def process_response(self, request, response):
        if response.status_code in [301, 302]:
            if request.COOKIES.get('hash_compat'):
                hash_part = urllib.unquote(request.COOKIES.get('hash_compat'))
                if hash_part and hash_part.startswith('#') and '#' not in response['Location']:
                    response['Location'] += hash_part
        return response
