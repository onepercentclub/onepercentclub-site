import logging
import re
import time
import os
import urllib
import urlparse
import tempfile

from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.utils import html as html_utils

from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.utils import is_connectable
from selenium.webdriver.phantomjs.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver


logger = logging.getLogger(__name__)


HASHBANG = '#!'
ESCAPED_FRAGMENT = '_escaped_fragment_'


class DedicatedWebDriver(RemoteWebDriver):
    """
    Wrapper to communicate with a dedicated PhantomJS through Ghostdriver.

    If you have a phantomjs instance running at all times, you can use this dedicated webdriver to communicate with it.
    """
    def __init__(self, port=None, desired_capabilities=DesiredCapabilities.PHANTOMJS):

        if port is None:
            port = 8910

        class DummyService():
            """Dummy service to accept the same calls as the PhantomJS webdriver."""
            def __init__(self, port):
                self.port = port

            @property
            def service_url(self):
                return 'http://localhost:%d/wd/hub' % port

            def stop(self, *args, **kwargs):
                pass

        self.service = DummyService(port)

        # Start the remove web driver.
        try:
            RemoteWebDriver.__init__(self,
                command_executor=self.service.service_url,
                desired_capabilities=desired_capabilities)
        except:
            self.quit()
            raise


        self._is_remote = False


class WebCache(object):
    """
    Class to make sure the web driver is lazily loaded. For regular requests, the driver should not be instantiated
    because it significantly slows down the request/response cycle (it can easily take 10 seconds to start).
    """

    _web_driver = None

    def __init__(self):
        if hasattr(settings, 'CRAWLABLE_PHANTOMJS_ARGS') and settings.CRAWLABLE_PHANTOMJS_ARGS:
            service_args = settings.CRAWLABLE_PHANTOMJS_ARGS[:]
        else:
            service_args = [
                '--load-images=false',
                '--disk-cache=true',
                '--local-storage-path=%s' % os.path.join(tempfile.gettempdir(), 'phantomjs')
            ]

        self.service_args = service_args

    def get_driver(self):
        """
        Only creates the driver if not present and returns it.

        :return: ``WebDriver`` instance.
        """

        # Dedicated mode
        if hasattr(settings, 'CRAWLABLE_PHANTOMJS_DEDICATED_MODE') and settings.CRAWLABLE_PHANTOMJS_DEDICATED_MODE:
            if not self._web_driver:
                self._web_driver = DedicatedWebDriver(
                    port=getattr(settings, 'CRAWLABLE_PHANTOMJS_DEDICATED_PORT', 8910)
                )
            elif not is_connectable(self._web_driver.service.port):
                raise RuntimeError('Cannot connect to dedicated PhantomJS instance on: %s' %
                                    self._web_driver.service.service_url)
        # Instance based mode (more for testing purposes). When debugging, you can even replace the PhantomJS webdriver
        # with firefox and remove the arguments to the web driver constructor below.
        else:
            if not self._web_driver:
                self._web_driver = WebDriver(service_args=self.service_args)
            elif not is_connectable(self._web_driver.service.port):
                self._web_driver.service.stop()
                self._web_driver = WebDriver(service_args=self.service_args)

        return self._web_driver


# Create a single instance per process.
web_cache = WebCache()


class HashbangMiddleware(object):
    """
    Middleware that catches requests with escaped fragments, like: http://example.com/?_escaped_fragment_=/projects

    These special cases are most likely requested by search engines that detected hashbangs (#!) in the URL. If such a
    request is made, the dynamic content is generated in the background, and the generated page source is served to the
    search engine.
    """

    def process_request(self, request):
        if request.method == 'GET' and ESCAPED_FRAGMENT in request.GET:
            original_url = request.build_absolute_uri()
            parsed_url = urlparse.urlparse(original_url)

            # Update URL with hashbang.
            query = dict(urlparse.parse_qsl(parsed_url.query))
            path = ''.join([parsed_url.path, HASHBANG, query.get(ESCAPED_FRAGMENT, '')])

            # Update query string by removing the escaped fragment.
            if ESCAPED_FRAGMENT in query:
                del query[ESCAPED_FRAGMENT]
            query = urllib.urlencode(query)

            # Build new absolute URL.
            absolute_url = urlparse.urlunparse([
                parsed_url.scheme,
                parsed_url.netloc,
                path,
                parsed_url.params,
                query,
                parsed_url.fragment
            ])

            try:
                driver = web_cache.get_driver()
                logger.debug('Generating flat content from "%s" for "%s".', absolute_url, original_url)
                driver.get(absolute_url)

                # TODO: This should be replaced with something smart that waits for a certain trigger that all JS
                # is done.
                time.sleep(3)

                content = driver.page_source
                # Remove all javascript, since its mostly useless now.
                script_tags_template = re.compile(r'<script([^/]*/>|(\s+[^>]*><\/script>))', re.U)
                content = script_tags_template.sub('', content)
            except Exception, e:
                logger.error('There was an error rendering "%s" for "%s" with the web driver: %s', absolute_url, original_url, e)
                return HttpResponseServerError()

            return HttpResponse(content=content)

        return None