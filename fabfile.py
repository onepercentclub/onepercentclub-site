"""
Fabfile for deploying Project Bluebottle.

This file is structured as follows:

    1. Environment settings
    2. Utility functions
    3. Fabric tasks

"""

from git import Repo

from fabric.api import (
    env, roles, sudo, prefix, cd, task, require, run, local, put,
    prompt, abort
)
from fabric.contrib.console import confirm
from fabric.colors import green, red

from contextlib import contextmanager


""" Configuration settings """
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

# Migrated data
env.migrated_data_root = '/var/lib/jenkins/jobs/legacydb/lastStable/archive/'
env.migrated_media_file = 'migrated_media.tar'
env.migrated_media_path = env.migrated_data_root + env.migrated_media_file
env.migrated_db_file = 'migrated_data.sql.bz2'
env.migrated_db_path = env.migrated_data_root + env.migrated_db_file
env.migration_server = 'localdev'

# By default, confirm everywhere
env.noinput = False


""" Utility functions """
@contextmanager
def virtualenv():
    """
    Make sure everything is executed from within the virtual environment.

    Example::

        with virtualenv():
            run('./manage.py collectstatic')

    """
    with cd(env.directory):
        with prefix('source env/bin/activate'):
            yield


def set_django_settings():
    """ Environment-dependant Django settings. """
    environment = env.host.split('.', 1)[0]
    env.django_settings = 'bluebottle.settings.%s' % environment


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
        abort('Commit not in branch %s' % env.deploy_branch)

    return commit


def tag_commit(commit_id, tag):
    """
    Tag the specified commit and push it to the server.
    Overwriting old tags with the same name.
    """
    local('git tag %s %s' % (tag, commit_id))
    local('git push --tags origin %s' % tag)


def make_versioned_tag(tag, version):
    """ Generate a versioned version of a tag. """

    return '%s-%d' % (tag, version)


def find_latest_tag_version(tag):
    """ Find the latest version for the given tag. Returns an integer. """

    r = Repo()

    version = 1
    while make_versioned_tag(tag, version+1) in r.tags:
        version += 1

    status_update(
        'Latest version for tag %s is %d: %s' % \
            (tag, version, make_versioned_tag(tag, version))
    )

    return version


def find_available_tag(tag):
    """
    Find the latest available version for a versioned tag of the form tag-N.
    """

    latest_version = find_latest_tag_version(tag)

    new_tag = make_versioned_tag(tag, latest_version+1)

    return new_tag


def confirm_deploy(commit):
    """ Confirm the deployment. """
    require('noinput')

    if not env.noinput:
        confirmed = confirm(
            'Are you sure you want to deploy %s?' % commit.hexsha, default=False
        )

        if not confirmed:
            abort('Confirmation required to continue.')


def confirm_extract_migrated_media():
    """ Confirm deleting existing media files. """
    require('noinput')

    status_update('Extracting media files.')

    if not env.noinput:
        confirmed = confirm(
            'This will overwrite existing media files. Are you sure?',
            default=False
        )

        if not confirmed:
            abort('Confirmation required to continue.')


def confirm_recreate_db(database):
    """ Confirm recreation of the database. """
    require('noinput')

    status_update('Recreating database.')

    if not env.noinput:
        confirmed = confirm(
            'This will completely destroy the database %s. Are you sure?' % \
            database, default=False
        )

        if not confirmed:
            abort('Confirmation required to continue.')


def confirm_wrong_tag(commit, tag):
    """ Confirm deployment when commit does not have expected tag. """

    print(red('WARNING: This commit does not have the %s tag.' % tag))

    if not env.noinput:
        confirmed = confirm(
            'Are you really sure you want to deploy %s?' % commit.hexsha,
            default=False
        )

        if not confirmed:
            abort('Confirmation required to continue.')


def confirm_prune_unref_files(unreferenced_files):
    """ Confirm pruning of unreferenced files. Returns boolean. """

    if not env.noinput:
        return confirm(
            'Do you want to prune %d unreferenced files?' % \
                len(unreferenced_files),
            default=False
        )

    # No confirmation needed, always return True.
    return True


def prompt_role():
    """
    Query the user for the role (and thus host) to use and store results in env.
    """
    if not env.host_string:
        role_options = ', '.join([role for role in env.roledefs.keys()])

        def validate(value):
            if not value in env.roledefs.keys():
                raise Exception('Role should be one of %s' % role_options)

            return value

        role = prompt(
            'Please specify a role (one of %s): ' % role_options,
            validate=validate
        )

        # Warning: this is a rather hackish solution - Fabric doesn't seem
        # to like the hosts for a task to be changed in the middle of a
        # process. This works ok, but limits us to one host per role.
        assert len(env.roledefs[role]) == 1, \
            'This is a hackish solution that does not work for a role with multiple hosts.'

        env.host = env.roledefs[role][0]
        env.host_string = env.host


def confirm_sync_migrated_data():
    status_update('Synching migrated data to %s.' % env.host_string)

    if not env.noinput:
        confirmed = confirm(
            'Do you want to load to the latest migrated data?',
            default=False
        )

        if not confirmed:
            abort('Confirmation required to continue.')


def extract_migrated_media():
    """ Extract migrated media. """
    confirm_extract_migrated_media()

    with cd(env.directory):
        run_web('tar xmf %s' % env.migrated_media_file)


def sync_migrated_media():
    """ Sync media of latest stable migration. """
    require('user')
    require('migration_server')
    require('migrated_media_path')
    require('migrated_media_file')

    # Sync data as the web user
    with cd(env.directory):
        run('rsync --inplace %s@%s:%s .' % (
            env.user, env.migration_server, env.migrated_media_path
        ))

        # Make sure the web user can read the file
        run('chmod g+r %s' % env.migrated_media_file)


def sync_migrated_db():
    """ Sync database for latest stable migration. """
    require('user')
    require('migration_server')
    require('migrated_db_path')
    require('migrated_db_file')

    with cd(env.directory):
        run('rsync --inplace %s@%s:%s .' % (
            env.user, env.migration_server, env.migrated_db_path
        ))

        # Make sure the web user can read the file
        run('chmod g+r %s' % env.migrated_db_file)


def recreate_db(database):
    """ Drop and create a database. """
    confirm_recreate_db(database)

    run_web('dropdb %s' % database)
    run_web('createdb -T template0 -E utf8 %s ' % database)


def load_dbdump(database, dbdump):
    """ Load up a database dump. """

    with cd(env.directory):
        run_web('bunzip2 -c %s | psql -q %s' % (
            dbdump, database
        ))


def assert_release_tag(commit, tag):
    """
    Make sure the given commit has the given tag and confirm if not so.

    It turns out there is no elegant and efficient way to do this without
    resorting to Perl-like shell scripts.

    Ref: http://stackoverflow.com/questions/4545370/how-to-list-all-tags-pointing-to-a-specific-commit-in-git
    """

    r = Repo()

    for current_tag in r.tags:
        if current_tag.commit == commit:
            # This tag refers to current commit

            if tag in current_tag.name:
                # The required tag is found, bail out
                return

    # It's not found, yield a warning
    confirm_wrong_tag(commit, tag)


def git_fetch_local():
    """ Fetch local GIT updates. """
    local('git fetch -q')


def update_git(commit_id):
    """ Update the repo to given commit_id. """
    require('directory')

    status_update('Updating git repository to %s.' % commit_id)

    with cd(env.directory):
        # Make sure only to fetch the required branch
        # This script should fail if we are updating to a non-deploy commit
        run('git fetch -q -t origin %s' % env.deploy_branch)
        run('git checkout -q %s' % commit_id)


def update_tar(commit_id):
    """ Update the remote to given commit_id using tar. """
    require('directory')

    status_update('Transferring archive of commit %s.' % commit_id)

    filename = '%s.tbz2' % commit_id
    local('git archive %s | bzip2 -c > %s' % (commit_id, filename))
    put(filename, env.directory)

    with cd(env.directory):
        run('tar xjf %s' % filename)
        run('rm %s' % filename)

    local('rm -f %s' % filename)


def prune_unreferenced_files():
    """
    Prune unreferenced files.

    WARNING: This deletes cached thumbnails as well. This should be fixed and
    not used until.
    """

    # Find unreferenced files
    with virtualenv():
        unreferenced_files = run_web('./manage.py unreferenced_files --settings=%s' % \
            env.django_settings
        ).splitlines()

    # If found, prompt for deletion
    if unreferenced_files:
        if confirm_prune_unref_files(unreferenced_files):
            status_update('Pruning %d unreferenced files' % len(unreferenced_files))

            for unref_file in unreferenced_files:
                run_web('rm %s' % unref_file)


def prepare_django():
    """ Prepare a deployment. """
    set_django_settings()

    require('django_settings')

    status_update('Preparing deployment.')

    with virtualenv():
        # TODO: Filter out the following messages:
        # "Could not find a tag or branch '<commit_id>', assuming commit."
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

        # Disabled for now; it unjustly deletes cached thumbnails
        # prune_unreferenced_files()


def restart_site():
    """ Gracefully restart gunicorn using supervisor. """
    require('service_name')

    run('supervisorctl restart %s' % env.service_name)


""" Fabric tasks """
@task
def sync_migrated_data():
    """ Sync data of latest stable migration. """

    # Prompt the user for a role (if not already set)
    prompt_role()

    # Confirm commit with user
    confirm_sync_migrated_data()

    sync_migrated_media()
    sync_migrated_db()

    extract_migrated_media()

    require('database')
    recreate_db(env.database)

    require('migrated_db_file')
    load_dbdump(env.database, env.migrated_db_file)


@task
def create_superuser():
    """ Create a Django superuser. """
    # Prompt the user for a role (if not already set)
    prompt_role()

    require('host_string')

    status_update('Creating Django user for %s' % env.host_string)

    set_django_settings()

    require('django_settings')

    with virtualenv():
        run_web('./manage.py createsuperuser --settings=%s' % \
            env.django_settings
        )


@roles('dev')
@task
def deploy_dev(revspec=None):
    """
    Update the dev server to the specified revspec, or HEAD of deploy branch.
    """
    # Don't ask for confirmation
    env.noinput = True

    # Update git locally
    git_fetch_local()

    # Find commit for revspec
    commit = find_commit(revspec)

    # Make sure the remote git repo is up to date
    update_git(commit.hexsha)

    # Get Django ready
    prepare_django()

    # Sync migrated data
    sync_migrated_data()

    # Restart app server
    restart_site()


@roles('testing')
@task
def deploy_testing(revspec=None):
    """
    Update the testing server to the specified revspec, or HEAD of deploy branch and optionally sync migrated data.
    """
    # Update git locally
    git_fetch_local()

    # Find commit for revspec
    commit = find_commit(revspec)
    tag = find_available_tag('testing')

    # Confirm commit with user
    confirm_deploy(commit)

    # Make sure the remote git repo is up to date
    update_git(commit.hexsha)

    # Get Django ready
    prepare_django()

    # Restart app server
    restart_site()

    # Deploy complete, tag commit
    tag_commit(commit.hexsha, tag)

    # Optionally, sync migrated data
    sync_migrated_data()


@roles('staging')
@task
def deploy_staging(revspec=None):
    """
    Update the staging server to the specified revspec, or the latest testing release and optionally sync migrated data.
    """

    # Update git locally
    git_fetch_local()

    # Find revspec or latest testing release
    if not revspec:
        version = find_latest_tag_version('testing')
        revspec = make_versioned_tag('testing', version)

    # Find commit for revspec
    commit = find_commit(revspec)

    # Find latest available staging version
    tag = find_available_tag('staging')

    # Confirm commit with user
    confirm_deploy(commit)

    # Check whether this commit has been tested
    assert_release_tag(commit, 'testing')

    # Update the code
    update_tar(commit.hexsha)

    # Get Django ready
    prepare_django()

    # Restart app server
    restart_site()

    # Deploy complete, tag commit
    tag_commit(commit.hexsha, tag)

    # Optionally, sync migrated data
    sync_migrated_data()

