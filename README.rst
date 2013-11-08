1%Club's website 
================

This is 1%Club's website. This site is proudly built using `BlueBottle
<https://github.com/onepercentclub/bluebottle>`_, the crowdfundning and
crowdsourcing framework developed by the 1%Club.

.. image:: https://travis-ci.org/onepercentclub/onepercentclub-site.png?branch=master
   :target: https://travis-ci.org/onepercentclub/onepercentclub-site

Getting started
---------------

#. Make sure you have a recent Python distro (2.7+ recommended)
#. Make sure (a recent) `pip <http://pypi.python.org/pypi/pip>`_ is installed
#. Make sure (a recent) `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ is installed
#. Clone the repo
#. In the repo dir, execute the following (tested with Bash, might work with others as well)::

    ./prepare.sh

#. Configure your database in `onepercentclub/settings/secrets.py`.
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
chapter of `2 Scoops of Django <https://django.2scoops.org/>`_. The settings can be found in `onepercentclub/settings`:

    * `base.py`: Project defaults used in any settings environment.
    * `secrets.py`: Used for storing passwords, API keys etc. This is not stored in Git.
    * `local.py`: Local settings used in personal development environment. This is not stored in Git.
    * `jenkins.py`: Settings for our Jenkins setup.
    * `travis.py`: Settings for Travis CI.
    * `dev.py`: Settings for the development server.
    * `testing.py`: Settings for the testing server.
    * `production.py`: Settings for the testing server.

Specific settings can be used by setting the environment variable `DJANGO_SETTINGS_MODULE` to
`onepercentclub.settings.<settings name>`::

    export DJANGO_SETTINGS_MODULE=onepercentclub.settings.local

Alternately you can specify the settings manually when you use `./manage.py`::

    ./manage.py runserver --settings=onepercentclub.settings.local

Deployment
----------
For deployment, we're using `Fabric
<http://docs.fabfile.org/en/1.4.3/index.html>`_. In order to deploy, the user
should have his/her SSH public key authorized for the user `onepercentadmin`
on the development, testing, staging and production environments. After this
has been done, make sure you use the environment and run::

    fab --list

This will display all the available Fabric commands, which are defined in `fabfile.py <https://github.com/onepercentclub/onepercentclub-site/blob/onepercentsite/fabfile.py>`_.

To deploy the latest version on dev to testing:
    
    fab deploy_testing

To deploy an older version to staging, say we want to revert to staging-66:
  
    fab deploy_staging:revspec=staging-66

Same goes for production

Fixtures
--------
Some models have default data which can be loaded after you run syncdb
with this command::

    ./manage.py loaddata <name of json file without extension>

For example, this command loads the data for the Bluebottle geo app::

    ./manage.py loaddata region_subregion_country_data

You can find a list of data files with this command run from the onepercentclub-site
directory::

    find apps -name \*.json

Running Tests
-------------

***Frontend Javascript***

From the root of the application (node/npm required):

        npm install
        grunt (or grunt test:chrome)

This will install some npm & bower packages for dev & testing, and run the tests headless with PhantomJS using Karma. Karma is watching the test/ directory for changes.

License
-------
1%Club's website is distributed under a 3-clause BSD license. For more
information, please refer to the `license <https://github.com/onepercentclub/onepercentclub-site/blob/master/LICENSE>`_.
