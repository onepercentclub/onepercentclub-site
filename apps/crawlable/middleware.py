import logging
import time
from django.conf import settings
import os
import urllib
import urlparse
import tempfile

from django.http import HttpResponse, HttpResponseServerError

from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.utils import is_connectable
from selenium.webdriver.phantomjs.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver


logger = logging.getLogger(__name__)


UNESCAPED_FRAGMENT = '#!'
ESCAPED_FRAGMENT = '_escaped_fragment_'


class DedicatedWebDriver(RemoteWebDriver):
    """
    Wrapper to communicate with a dedicated PhantomJS through Ghostdriver.

    If you have a phantomjs instance running at all times, you can use this dedicated webdriver to communicate with it.
    """
    def __init__(self, port=None, desired_capabilities=DesiredCapabilities.PHANTOMJS):

        if port is None:
            port = 8910

        service_url = 'http://localhost:%d/wd/hub' % port

        try:
            RemoteWebDriver.__init__(self,
                command_executor=service_url,
                desired_capabilities=desired_capabilities)
        except:
            self.quit()
            raise

        class DummyService():
            def __init__(self, port):
                self.port = port

            def stop(self, *args, **kwargs):
                pass

        self.service = DummyService(port)
        self._is_remote = False


class WebCache(object):
    """
    Class to make sure the web driver is lazily loaded. For regular requests, the driver should not be instantiated
    because it significantly slows down the request/response cycle (it can easily take 10 seconds to start).
    """

    _web_driver = None

    def __init__(self):

        if settings.CRAWLABLE_PHANTOMJS_ARGS:
            service_args = settings.CRAWLABLE_PHANTOMJS_ARGS[:]
        else:
            service_args = [
                '--load-images=false',
                '--disk-cache=true',
                '--local-storage-path=%s' % os.path.join(tempfile.gettempdir(), 'phantomjs')
            ]

        self.service_args = service_args

    def get_driver(self):
        launch = False

        if self._web_driver is None:
            launch = True
        elif not is_connectable(self._web_driver.service.port):
            self._web_driver.service.stop()
            launch = True

        if launch:
            if settings.CRAWLABLE_PHANTOMJS_DEDICATED_MODE:
                self._web_driver = DedicatedWebDriver(port=settings.CRAWLABLE_PHANTOMJS_DEDICATED_PORT)
            else:
                self._web_driver = WebDriver(service_args=self.service_args)

        return self._web_driver


web_cache = WebCache()


class HashbangMiddleware(object):

    def process_request(self, request):
        if request.method == 'GET' and ESCAPED_FRAGMENT in request.GET:
            original_url = request.build_absolute_uri()
            parsed_url = urlparse.urlparse(original_url)

            # Update URL with hashbang.
            query = dict(urlparse.parse_qsl(parsed_url.query))
            path = ''.join([parsed_url.path, UNESCAPED_FRAGMENT, query[ESCAPED_FRAGMENT]])

            # Update query string by removing the escaped fragment.
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

                # Update the HTML content with the "escaped fragment"-style URLs.
                content = driver.page_source.replace('%s' % UNESCAPED_FRAGMENT, '?%s=' % ESCAPED_FRAGMENT)
            except Exception, e:
                logger.error('There was an error rendering "%s" for "%s" with the web driver: %s', absolute_url, original_url, e)
                return HttpResponseServerError()

            return HttpResponse(content=content)

        return None