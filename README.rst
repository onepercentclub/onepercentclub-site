bluebottle
=========

The central repository for the bluebottle project.

Getting started
---------------

1. Make sure you have a recent Python distro (2.7+ recommended)
2. Make sure (a recent) `pip <http://pypi.python.org/pypi/pip>`_ is installed
3. Make sure (a recent) `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ is installed
4. Clone the repo
5. In the repo dir, execute the following (tested with Bash, might work with others as well)::

    prepare.sh

6. Ready to rock with dev setup::

    runserver.sh

7. Alternately (and preferably), enable the newly created environment with the command::

    source env/bin/activate

Moreover
--------

Requirements for the virtual environment can be found in `requirements.txt` and
the environment itself is in `env` in the project's root dir. It is
automatically ignored through `.gitignore`.

Default Data
------------

Some models have default data which can be loaded after you run syncdb
with this command:

    ./manage.py loaddata <name of json file without extension>

For example, this command loads the default Project Categories:

    ./manage.py loaddata project_category_data

You can find a list of data files with this command run from the bluebottle
directory:

    find apps -name \*.json
