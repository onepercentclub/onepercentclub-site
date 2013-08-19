Continuous Integration
======================

Headless browser testing with Jenkins
-------------------------------------

All functional tests require Selenium. There is an option available in ``settings.py`` (or your version of it) that
enables the Selenium tests::

    SELENIUM_TESTS = True

There are two ways to enable headless browser testing on Jenkins.

PhantomJS
~~~~~~~~~

A little experimental but mostly does the job is to use PhantomJS. It should already be installed for the Crawlable app
in BlueBottle.

    SELENIUM_WEBDRIVER = 'phantomjs'

Firefox
~~~~~~~

More trustworthy is to use `Firefox`_. You can run test suites that require a GUI (like a web browser) on Jenkins.
Roughly speaking, `Xvfb`_ imitates a monitor and lets you run a real GUI application or web browser on a headless
machine, as if a proper display were attached. Together with the `Xvfb Plugin for Jenkins`_, tests can start an instance
of Firefox without a GUI.

1. Install `Xvfb`_ on the machine where Jenkins runs::

    $ sudo apt-get install xvfb

2. Install `Firefox`_ (not Iceweasel, and uninstall if present) on the same machine::

    $ wget http://download.cdn.mozilla.net/pub/mozilla.org/firefox/releases/23.0.1/linux-i686/en-US/firefox-23.0.1.tar.bz2
    $ tar -jxvf firefox-23.0.1.tar.bz2
    $ sudo chown -R root:users /opt/firefox
    $ sudo chmod 755 /opt/firefox
    $ sudo ln -s /opt/firefox/firefox /usr/local/bin/firefox

3. Chances are that you are trying to install the 32 bit version of firefox in a 64 bit Debian environment::

    ./firefox: error while loading shared libraries: libstdc++.so.6: cannot open shared object file: No such file or directory

   Install these libraries to fix this issue::

    $ sudo apt-get install ia32-libs ia32-libs-gtk

4. Set the Selenium webdriver (the browser instance to start) to Firefox in Django's ``settings.py``::

    SELENIUM_WEBDRIVER = 'firefox'

5. In Jenkins, install the `Xvfb Plugin for Jenkins`_.

   1. Go to ``Manage Jenkins`` > ``Manage Plugins`` and install the plugin.
   2. Add an ``Xvfb`` installation by going to ``Manage Jenkins`` > ``Configure System``.
   3. Go to your project configuration, and enable ``Xvfb``.

.. _Firefox: https://www.mozilla.org/en-US/firefox/all/
.. _Xvfb: http://packages.debian.org/sid/xvfb
.. _Xvfb Plugin for Jenkins: https://wiki.jenkins-ci.org/display/JENKINS/Xvfb+Plugin
