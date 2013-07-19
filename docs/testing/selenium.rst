Selenium
========

This section briefly discusses how developers can contribute with functional tests, using Selenium.

Introduction
------------

The Django test client allows for some functional testing using the `Django dummy client`_. Internally it routes all
requests to the views of your project. The responses are simply strings and no parsing takes place. The BlueBottle
project focuses heavily on JavaScript which is ignored by this client.

Enter Selenium. `Selenium`_ allows developers to write functional tests that happen in an actual browser (like Mozilla
Firefox). It has support for (and from) some the largest browser vendors. With Django 1.4+, it is possible to write
tests using Selenium that communicate to an actual (internal or remote) web server.

For the bulk testing purposes, we use a "headless" browser called `PhantomJS`_. PhantomJS can do most things a regular
browser can do but it does not need any graphical interface.

On top of this, we use `Splinter`_ which only creates a thin, more intuitive layer on top of Selenium. You can still use
all Selenium functions, if you want to.

.. _Selenium: http://www.seleniumhq.org/
.. _PhantomJS: http://phantomjs.org/
.. _Django dummy client: https://docs.djangoproject.com/en/dev/topics/testing/overview/#test-client
.. _Splinter: http://splinter.cobrateam.info/


Getting ready
-------------

Install `PhantomJS`_ on your development machine or (test) server. Additionally, install the regular browsers you want
to test in (Chrome, Firefox, Internet Explorer). Finally, if you want to test in Chrome or Internet Explorer, install
the `Chrome web-driver`_ and/or the `Internet Explorer web-driver`_.

.. note:: Chrome is recommended for development since Firefox does not support mouse interactions.

All these web-drivers need to be present in your path, for the tests to be able to use them.

.. _Chrome web-driver: https://code.google.com/p/chromedriver/downloads/list
.. _Internet Explorer web-driver: https://code.google.com/p/selenium/downloads/list

Install the requirements, if not already included by the ``requirements.txt`` file::

    $ source env/bin/activate
    $ pip install selenium splinter

Configure your Django settings or specifically, your ``bluebottle/settings/local.py``. The following configuration
options are available::

    SELENIUM_TESTS = True  # Set to False to skip all Selenium tests.
    SELENIUM_WEBDRIVER = 'firefox' # Can be any of chrome, firefox, phantomjs


Writing tests
-------------

Keep in mind to write tests that consider how and if the information is presented on the website as you would expect.

Consider the following test case:

.. code-block:: python
   :linenos:

    from django.conf import settings
    from django.utils.unittest.case import skipUnless

    from bluebottle.tests.utils import SeleniumTestCase


    @skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
    class ExampleSeleniumTests(SeleniumTestCase):

        def test_view_homepage(self):
            self.browser.visit(self.live_server_url)

            self.assertTrue(self.browser.is_text_present('CHOOSE YOUR PROJECT', wait_time=10))


As you may notice, the test class is decorated with a ``skipUnless`` function. This function checks whether you actually
want to run tests involving Selenium and should be on top of all your test classes that test with Selenium.

Furthermore, we extend from ``SeleniumTestCase``. This class is a wrapper around ``LiveServerTestCase`` and offers us
the ``self.browser`` property that emulates the browser. Some additional helper functions are also present which will
not be discussed here.

You can use any of the regular test mixins to add some data to your database, to make the tests work.

.. note:: It's not recommended to use a fixture due to the many changes in models, and the long loading times.

The first test is to simply open the homepage, by going to the ``self.live_server_url``, which represents the address
to the internal webserver. After changing telling the browser to visit this URL, we can check if some dynamically loaded
content is present on the web page. Actually, the parameter ``wait_time=10`` in the ``self.browser.is_text_present``
function tells this test function to wait a maximum of 10 seconds before the text "CHOOSE YOUR PROJECT" appears. If the
text appears earlier, your test will continue as soon as it appears.


Tips
----

A live server test case can be hard to debug. Below are some pointers to help debugging these tests.

1. Check the ``from django.utils.html`` for usefull utility functions, such as ``remove_tags``. With these you can
   manipulate the HTML and make it easier to compare values.

2. Use breakpoints in your IDE, and evaluate lines of code that interact with your browser to write a test. This
   prevents a lot of time spent on initializing the web driver and running the unit tests repeatedly.

3. Remember that you can use an actual browser to help you find problems. In Firefox and Chrome for example, you can use
   the developer tools.

4. You can `override settings`_ that are used in the settings file. For example, to show the uncompressed CSS and JS
   files, append the following line on top of your test function::

        @override_settings(COMPRESS_ENABLED=False)

.. _override settings: https://docs.djangoproject.com/en/dev/topics/testing/overview/#django.test.utils.override_settings


Common issues
-------------

You get the WebDriver exception: ``Adapter is either null or does not implement `findHasMany` method``.

    This is actually an Ember exception raised via JavaScript. Most likely, you are missing some data that is "required"
    on a certain page you are visiting. Launch the test in a non-headless browser and inspect the JavaScript errors.
