import sys

from git import Repo

from fabric.api import (
    env, roles, sudo, prefix, cd, task, require, run, local
)
from fabric.contrib.console import confirm
from fabric.colors import green

from contextlib import contextmanager

# If True, enables forwarding of your local SSH agent to the remote end.
env.forward_agent = True

# Assign the hosts to roles, for convenient reference and scaling
env.roledefs = {
    'staging': ['staging.onepercentclub.com'],
    'testing': ['testing.onepercentclub.com'],
    'dev': ['dev.onepercentclub.com']
}

# Admin user
env.user = 'onepercentadmin'

# User running the web service
env.web_user = 'onepercentsite'

# Directory (on the server) where our project will be running
env.directory = '/var/www/onepercentsite'

# Name of supervisor service
env.service_name = 'onepercentsite'

# Name of deployment branch
env.deploy_branch = 'onepercentsite'

# Name of the database
env.database = 'onepercentsite'

# Django settings used
env.django_settings = 'bluebottle.settings.user_testing'

# Migrated data
env.migrated_data_root = '/var/lib/jenkins/jobs/legacydb/lastStable/archive/'
env.migrated_media_file = 'migrated_media.tar'
env.migrated_media_path = env.migrated_data_root + env.migrated_media_file
env.migrated_db_file = 'migrated_data.sql.bz2'
env.migrated_db_path = env.migrated_data_root + env.migrated_db_file
env.migration_server = 'localdev'

# By default, confirm recreation of database
env.confirm_recreate_db = True


@contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix('source env/bin/activate'):
            yield


def run_web(*args, **kwargs):
    """ Run a command as the web user. """

    kwargs.setdefault('user', env.web_user)

    return sudo(*args, **kwargs)


def status_update(message):
    """ Print status update message. """

    print(green(message))


def find_commit(revspec=None):
    """
    Find the specified commit by revspec and check that it's in deploy_branch.
    """

    require('deploy_branch')

    local_deploy_branch = 'origin/' + env.deploy_branch

    if not revspec:
        revspec = local_deploy_branch

    r = Repo()

    # Get the commit from the repo
    commit = r.commit(revspec)
    status_update('Deploying commit %s: %s' % (commit.hexsha, commit.summary))

    # Check whether it's a deploy commit
    deploy_commits = r.iter_commits(local_deploy_branch)

    if not commit in deploy_commits:
        sys.exit('Commit not in branch %s' % env.deploy_branch)

    return commit


def tag_commit(commit_id, tag):
    """
    Tag the specified commit and push it to the server.
    Overwriting old tags with the same name.
    """
    local('git tag %s %s' % (tag, commit_id))
    local('git push --tags origin %s' % tag)


def find_available_tag(tag):
    """
    Find the latest available version for a versioned tag ofthe form tag-N.
    """

    def make_tag(tag, version):
        return '%s-%d' % (tag, version)

    r = Repo()

    version = 1
    new_tag = make_tag(tag, version)

    while new_tag in r.tags:
        version += 1
        new_tag = make_tag(tag, version)

    status_update(
        'Latest version for tag %s is %d: %s' % (tag, version, new_tag)
    )

    return new_tag


def confirm_deploy(commit):
    """ Confirm the deployment. """

    confirmed = confirm(
        'Are you sure you want to deploy %s?' % commit.hexsha, default=False
    )
    if not confirmed:
        sys.exit('Confirmation required to continue.')


def sync_migrated_media():
    """ Sync media of latest stable migration. """
    require('user')
    require('migration_server')
    require('migrated_media_path')
    require('migrated_media_file')

    # Sync data as the web user
    with cd(env.directory):
        run('rsync --inplace --chmod=g=r %s@%s:%s .' % (
            env.user, env.migration_server, env.migrated_media_path
        ))

        run_web('tar xmf %s' % env.migrated_media_file)


def sync_migrated_db():
    """ Sync database for latest stable migration. """
    require('user')
    require('migration_server')
    require('migrated_db_path')

    with cd(env.directory):
        run('rsync --inplace --chmod=g=r %s@%s:%s .' % (
            env.user, env.migration_server, env.migrated_db_path
        ))


def confirm_recreate_db(database):
    """ Confirm recreation of the database. """

    confirmed = confirm(
        'This will completely destroy the database %s. Are you sure?' % \
        database, default=False
    )

    if not confirmed:
        sys.exit('Confirmation required to continue.')


def recreate_db(database):
    """ Drop and create a database. """
    if env.confirm_recreate_db:
        confirm_recreate_db(database)

    run_web('dropdb %s' % database)
    run_web('createdb -T template0 -E utf8 %s ' % database)


def load_dbdump(database, dbdump):
    """ Load up a database dump. """

    with cd(env.directory):
        run_web('bunzip2 -c %s | psql -q %s' % (
            dbdump, database
        ))


@task
def sync_migrated_data():
    """ Sync data of latest stable migration. """

    status_update('Synching migrated data.')

    sync_migrated_media()
    sync_migrated_db()

    status_update('Reloading database.')

    require('database')
    recreate_db(env.database)

    require('migrated_db_file')
    load_dbdump(env.database, env.migrated_db_file)


@task
def git_fetch_local():
    """ Fetch local GIT updates. """
    local('git fetch -q')


@task
def update_git(commit_id):
    """ Update the repo to given commit_id. """
    require('directory')

    status_update('Updating git repository to %s.' % commit_id)

    with cd(env.directory):
        # Make sure only to fetch the required branch
        # This script should fail if we are updating to a non-deploy commit
        run('git fetch -q -t origin %s' % env.deploy_branch)
        run('git checkout -q %s' % commit_id)


@task
def prepare_django():
    """ Prepare a deployment. """
    require('django_settings')

    status_update('Preparing deployment.')

    with virtualenv():
        run('pip install -q -r requirements.txt')

        run('./manage.py compile_pyc')

        # Disabled until the following problem is fixed:
        # ERROR: test_site_profile_not_available (django.contrib.auth.tests.models.ProfileTestCase)
        #run_web('./manage.py test -v 0')

        run_web('./manage.py syncdb --migrate -v 0 --noinput --settings=%s' % \
            env.django_settings
        )
        run_web('./manage.py collectstatic -l -v 0 --noinput --settings=%s' % \
            env.django_settings
        )


@task
def restart_site():
    """ Gracefully restart gunicorn using supervisor. """
    require('service_name')

    run('supervisorctl restart %s' % env.service_name)


@task
def create_superuser():
    """ Create a Django superuser. """
    require('django_settings')

    with virtualenv():
        run_web('./manage.py createsuperuser --settings=%s' % \
            env.django_settings
        )


@roles('testing')
@task
def deploy_testing(revspec=None):
    """
    Update the testing server to the specified revspec, or default to the
    local HEAD of onepercentsite.

    1. Pull
    2. Checkout the requested commi
    3. Update Python requirements
    4. Run the unittests
    5. Run database migrations
    6. Collect static files
    7. Restart the app server
    """
    require('deploy_branch')

    # Update git locally
    git_fetch_local()

    # Find commit for revspec
    commit = find_commit(revspec)
    tag = find_available_tag('testing')

    # Confirm commit with user
    confirm_deploy(commit)

    # Make sure the remote git repo is up to date
    update_git(commit)

    # Get Django ready
    prepare_django()

    # Restart app server
    restart_site()

    # Deploy complete, tag commit
    tag_commit(commit.hexsha, tag)


@roles('dev')
@task
def deploy_dev(revspec=None):
    """
    Update the dev server to the specified revspec, or default to the
    local HEAD of onepercentsite.
    """
    require('deploy_branch')

    # Update git locally
    git_fetch_local()

    # Find commit for revspec
    commit = find_commit(revspec)

    # Make sure the remote git repo is up to date
    update_git(commit)

    # Get Django ready
    prepare_django()

    # Sync migrated data
    env.confirm_recreate_db = False
    sync_migrated_data()

    # Restart app server
    restart_site()
