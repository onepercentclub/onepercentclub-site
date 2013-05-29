Project Bluebottle
==================

The repository for Project Bluebottle, the crowdsourcing framework initiated
by the 1%CLUB.

:build status: |build-image|

.. |build-image| image:: https://travis-ci.org/onepercentclub/bluebottle.png?branch=master
                 :target: https://travis-ci.org/onepercentclub/bluebottle

Getting started
---------------

#. Make sure you have a recent Python distro (2.7+ recommended)
#. Make sure (a recent) `pip <http://pypi.python.org/pypi/pip>`_ is installed
#. Make sure (a recent) `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ is installed
#. Clone the repo
#. In the repo dir, execute the following (tested with Bash, might work with others as well)::

    ./prepare.sh

#. Configure your database in `bluebottle/settings/secrets.py`.
#. Activate the newly created environment in `env`::

    source env/bin/activate

#. Update database structure::

    ./manage.py syncdb --migrate

#.  You're ready to roll now, baby!

Requirements and environment
----------------------------

Requirements for the virtual environment can be found in `requirements.txt`
and the environment itself is in `env` in the project's root dir. It is
automatically ignored through `.gitignore`.

Translations
------------
Translations are managed using Transifex. Feel free to contribute and
collaborate at the
`Transifex project page <https://www.transifex.com/projects/p/bluebottle/>`_.

Settings
--------
Bluebottle has different settings for different environments as described in the "Settings and Requirements Files"
chapter of `2 Scoops of Django <https://django.2scoops.org/>`_. The settings can be found in `bluebottle/settings`:

    * `base.py`: Project defaults used in any settings environment.
    * `secrets.py`: Used for storing passwords, API keys etc. This is not stored in Git.
    * `local.py`: Local settings used in personal development environment. This is not stored in Git.
    * `jenkins.py`: Settings for our Jenkins setup.
    * `travis.py`: Settings for Travis CI.
    * `dev.py`: Settings for the development server.
    * `testing.py`: Settings for the testing server.
    * `production.py`: Settings for the testing server.

Specific settings can be used by setting the environment variable `DJANGO_SETTINGS_MODULE` to
`bluebottle.settings.<settings name>`::

    export DJANGO_SETTINGS_MODULE=bluebottle.settings.local

Alternately you can specify the settings manually when you use `./manage.py`::

    ./manage.py runserver --settings=bluebottle.settings.local



Fixtures
--------
Some models have default data which can be loaded after you run syncdb
with this command::

    ./manage.py loaddata <name of json file without extension>

For example, this command loads the data for the Bluebottle geo app::

    ./manage.py loaddata region_subregion_country_data

You can find a list of data files with this command run from the bluebottle
directory::

    find apps -name \*.json

License
-------
Project Bluebottle is distributed under a 3-clause BSD license. For more
information, please refer to the `license <https://github.com/onepercentclub/bluebottle/blob/master/LICENSE>`_.
