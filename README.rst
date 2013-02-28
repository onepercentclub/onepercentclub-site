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
The project has settings for every environment in the DTAP scheme. They can be
found in `bluebottle/settings`:

    * `jenkins.py`: Settings for continuous integration environment.
    * `dev.py`: Settings for development environment.
    * `testing.py`: Settings for testing environment.
    * `staging.py`: Settings for staging environment.
    * `production.py`: Production settings.

Specific settings can be used by setting the environment variable
`DJANGO_SETTINGS_MODULE` to `bluebottle.settings.environment`::

    export DJANGO_SETTINGS_MODULE=bluebottle.settings.production

Apart from these environment specific settings, the following settings exist:

    * `defaults.py`: Project defaults used in any settings environment.
    * `secrets.py`: Used for storing passwords, API keys etcetera, kept out of the scope of Git.
    * `local.py`: Local settings overrides, based off `defaults.py`. Not stored in Git.

If no settings are explicitly chosen using `DJANGO_SETTINGS_MODEL`, the
`local.py` settings are loaded, defaulting to override `defaults.py`
settings.

When not using the default settings imported from `local.py`, you must ensure that `local.py`
is an empty file otherwise the site will not work properly.

Rationale
*********
As to allow for convenient overriding a chaining import pattern is used, where
the used settings (ie. `local.py`) imports more generic settings which, in
turn, imports more generic settings. The exception being `secrets.py` which
should be minimal and should not require other settings to be available. For
more information on the used settings pattern, consult the
`SplitSettings <https://code.djangoproject.com/wiki/SplitSettings#SimplePackageOrganizationforEnvironments>`_
page in the Django Wiki.

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
