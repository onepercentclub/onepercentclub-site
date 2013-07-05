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

Install the requirements, if not already included by the ``requirements.txt`` file::

    $ source env/bin/activate
    $ pip install selenium splinter


Creating test data
------------------

Optionally, we can create a dump of our database (make sure you obfuscate production or sensitive data) with Django. To
make a usable dump, we use natural keys and leave out some tables that are created and filled during the database
creation process in our unit tests.

To clean up the database, we can delete everything older than 60 days. In a Python shell:

.. code-block:: python
   :linenos:

    import datetime
    delete_date = datetime.datetime.now() - datetime.timedelta(days=60)
    max_projects = 100
    max_tags = 100
    max_wallposts = 100

    from apps.projects.models import Project
    Project.objects.filter(created__lt=delete_date).delete()
    Project.objects.exclude(pk__in=Project.objects.values_list('pk', flat=True)[:max_projects]).delete()

    from apps.organizations.models import Organization
    Organization.objects.filter(projectplan=None).delete()

    from apps.fund.models import Order
    Order.objects.filter(updated__lt=delete_date).delete()

    from taggit.models import Tag
    Tag.objects.exclude(pk__in=Tag.objects.all()[:max_tags].values_list('pk', flat=True)).delete()

    # Polymorphic models don't work well with dumpdata/loaddata.
    from apps.wallposts.models import WallPost, TextWallPost, MediaWallPost, Reaction
    wallpost_pk_set = WallPost.objects.filter(created__lt=delete_date).values_list('pk', flat=True)[:max_wallposts]

    TextWallPost.objects.exclude(wallpost_ptr__in=wallpost_pk_set).delete()
    MediaWallPost.objects.filter(wallpost_ptr__in=wallpost_pk_set).delete()
    WallPost.objects.exclude(pk__in=wallpost_pk_set).delete()

    Reaction.objects.all().delete()

    from apps.accounts.models import BlueBottleUser
    BlueBottleUser.objects.filter(wallpost_wallpost=None, owner=None, taskmember=None, team_member=None, donation=None).delete()

It may take a while to generate the demo data, make sure it's not already included with the source code::

    $ python manage.py dumpdata --exclude=sessions --exclude=contenttypes --exclude=auth.Permission \
        --exclude=south --exclude=admin.LogEntry --natural --format=json --indent=2 > bluebottle/fixtures/demo.json
    $ gzip bluebottle/fixtures/demo.json

You can also create test data inside your test class. However, since we are testing the "real" website, you may find
yourself creating a lot of data to get anywhere (menu's, users, projects, etc.).


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
        fixtures = ['demo',]

        def test_view_homepage(self):
            self.browser.visit(self.live_server_url)

            self.assertTrue(self.browser.is_text_present('CHOOSE YOUR PROJECT', wait_time=10))


As you may notice, the test class is decorated with a ``skipUnless`` function. This function checks whether you actually
want to run tests involving Selenium and should be on top of all your test classes that test with Selenium.

Furthermore, we extend from ``SeleniumTestCase``. This class is a wrapper around ``LiveServerTestCase`` and offers us
the ``self.browser`` property that emulates the browser. Some additional helper functions are also present which will
not be discussed here.

A fixture is included that holds some basic information on all parts of the website. This makes it possible to test
something.

The first test is to simply open the homepage, by going to the ``self.live_server_url``, which represents the address
to the internal webserver. After changing telling the browser to visit this URL, we can check if some dynamically loaded
content is present on the web page. Actually, the parameter ``wait_time=10`` in the ``self.browser.is_text_present``
function tells this test function to wait a maximum of 10 seconds before the text "CHOOSE YOUR PROJECT" appears. If the
text appears earlier, your test will continue as soon as it appears.


Tips
----

1. Check the ``from django.utils.html`` for usefull utility functions, such as ``remove_tags``. With these you can
   manipulate the HTML and make it easier to compare values.


Debugging
---------

A live server test case can be hard to debug. Below are some pointers to help debugging these tests.

1. Remember that you can use an actual browser to help you find problems. In Firefox and Chrome for example, you can use
   the developer tools.

2. You can `override settings`_ that are used in the settings file. For example, to show the uncompressed CSS and JS
   files, append the following line on top of your test function::

        @override_settings(COMPRESS_ENABLED=False)

.. _override settings: https://docs.djangoproject.com/en/dev/topics/testing/overview/#django.test.utils.override_settings