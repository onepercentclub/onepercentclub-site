# Fabfile for deploying Project Bluebottle.
#
# This file is structured as follows:
#
#    1. Environment settings
#    2. Utility functions
#    3. Fabric tasks

from git import Repo
from fabric.api import env, roles, sudo, prefix, cd, task, require, run, local, put, prompt, abort
from fabric.contrib.console import confirm
from fabric.colors import green, red
from fabric.operations import get
from contextlib import contextmanager


# Configuration settings:
# If True, enables forwarding of your local SSH agent to the remote end.
env.forward_agent = True

# Assign the hosts to roles, for convenient reference and scaling
env.roledefs = {
    'production': ['production.onepercentclub.com'],
    'staging': ['staging.onepercentclub.com'],
    'testing': ['testing.onepercentclub.com'],
    'dev': ['dev.onepercentclub.com'],
    'backup': ['backups@bluebucket.onepercentclub.com']
}

# Admin user
env.user = 'onepercentadmin'

# User running the web service
env.web_user = 'onepercentsite'

# Directory (on the server) where our project will be running
env.directory = '/var/www/onepercentsite'

# Name of supervisor service
env.service_name = 'onepercentsite'

# Name of the database
env.database = 'onepercentsite'

# By default, confirm everywhere
env.noinput = False


# Utility functions:
@contextmanager
def virtualenv():
    """
    Make sure everything is executed from within the virtual environment.

    Example::

        with virtualenv():
            run('./manage.py collectstatic')

    """
    require('directory')

    with cd(env.directory):
        with prefix('source env/bin/activate'):
            yield


def set_django_settings():
    """ Environment-dependant Django settings. """
    require('host')
    environment = env.host.split('.', 1)[0]
    env.django_settings = 'onepercentclub.settings.%s' % environment


def run_web(*args, **kwargs):
    """ Run a command as the web user. """
    require('web_user')

    kwargs.setdefault('user', env.web_user)

    return sudo(*args, **kwargs)


def status_update(message):
    """ Print status update message. """

    print(green(message))


def get_commit_tags(commit):
    """ Get all tags for a commit. """

    r = Repo()

    tags = set()

    for tag in r.tags:
        if tag.commit == commit:
            tags.add(tag.name)

    return tags


def describe_commit(commit):
    """
    Return a verbose commit name based on shortened hash, tags and summary.
    """

    tags = ' '.join(get_commit_tags(commit))

    if tags:
        return '%s %s: %s' % (commit.hexsha[:7], tags, commit.summary)
    else:
        return '%s: %s' % (commit.hexsha[:7], commit.summary)


def get_commit(revspec):
    """
    Find the specified commit by revspec.
    """

    r = Repo()

    # Get the commit from the repo
    commit = r.commit(revspec)
    status_update('Deploying commit %s' % describe_commit(commit))

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


def confirm_wrong_tag(commit, tag):
    """ Confirm deployment when commit does not have expected tag. """
    require('noinput')

    print(red('WARNING: This commit does not have the %s tag.' % tag))

    if not env.noinput:
        confirmed = confirm('Are you really sure you want to deploy %s?' % commit.hexsha, default=False)

        if not confirmed:
            abort('Confirmation required to continue.')


def prompt_role():
    """
    Query the user for the role (and thus host) to use and store results in env.
    """
    require('roledefs')

    if not env.host_string:
        role_options = ', '.join([role for role in env.roledefs.keys()])

        def validate(value):
            if not value in env.roledefs.keys():
                raise Exception('Role should be one of %s' % role_options)

            return value

        role = prompt('Please specify a role (one of %s): ' % role_options, validate=validate)

        # Warning: this is a rather hackish solution - Fabric doesn't seem
        # to like the hosts for a task to be changed in the middle of a
        # process. This works ok, but limits us to one host per role.
        assert len(env.roledefs[role]) == 1, \
            'This is a hackish solution that does not work for a role with multiple hosts.'

        env.host = env.roledefs[role][0]
        env.host_string = env.host


def assert_release_tag(commit, tag):
    """
    Make sure the given commit has the given tag and confirm if not so.
    """

    tags = get_commit_tags(commit)

    # Match a single string as to ignore versions in "tag-<VERSION>"
    if not tag in ' '.join(tags):
        # It's not found, confirm with user
        confirm_wrong_tag(commit, tag)


def git_fetch_local():
    """ Fetch local GIT updates. """
    local('git fetch -q')


def update_git(commit):
    """ Update the repo to given commit_id. """
    require('directory')

    status_update('Updating git repository to %s' % describe_commit(commit))

    with cd(env.directory):
        # Make sure only to fetch the required branch
        # This script should fail if we are updating to a non-deploy commit
        run('git fetch -q -p')
        run('git checkout -q %s' % commit.hexsha)


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
    require('directory')

    # Find unreferenced files
    with virtualenv():
        unreferenced_files = run_web('./manage.py unreferenced_files --settings=%s' % \
            env.django_settings
        ).splitlines()

    # If found, prompt for deletion
    if unreferenced_files:
        status_update('Pruning %d unreferenced files' % len(unreferenced_files))

        for unref_file in unreferenced_files:
            run_web('rm %s' % unref_file)

def add_git_commit():
    with cd(env.directory):
        run('echo "GIT_COMMIT = \'`git log --oneline | head -n1 | cut -c1-7`\'" >> onepercentclub/settings/base.py')

def prepare_django():
    """ Prepare a deployment. """
    set_django_settings()

    require('django_settings')

    status_update('Preparing deployment.')

    with virtualenv():
        # TODO: Filter out the following messages:
        # "Could not find a tag or branch '<commit_id>', assuming commit."
        run('pip install -q --allow-all-external --allow-unverified django-admin-tools -r requirements/requirements.txt')

        # Remove and compile the .pyc files.
        run('find . -name \*.pyc -delete')
        run('./manage.py compile_pyc --settings=%s' % env.django_settings)

        # Prepare the translations.
        run('./translations.sh compile %s' % env.django_settings)

        # Disabled until the following problem is fixed:
        # ERROR: test_site_profile_not_available (django.contrib.auth.tests.models.ProfileTestCase)
        #run_web('./manage.py test -v 0')

        # Make sure the web user can read and write the static media dir.
        run('chmod a+rw static/media')

        run_web('./manage.py syncdb --migrate --noinput --settings=%s' % env.django_settings)
        run_web('./manage.py collectstatic --clear -l -v 0 --noinput --settings=%s' % env.django_settings)

        # Disabled for now; it unjustly deletes cached thumbnails
        # prune_unreferenced_files()


def restart_site():
    """ Gracefully restart gunicorn using supervisor. """
    require('service_name')

    run('supervisorctl restart %s' % env.service_name)


def set_site_domain():
    """ Set the site domain dependent on env.host. """

    status_update('Updating domain for default Django Site to %s' % env.host)

    set_django_settings()
    require('django_settings')
    require('host')

    if 'production' in env.host:
        host = 'onepercentclub.com'
    else:
        host = env.host

    sites_command = (
        "from django.contrib.sites.models import Site; "
        "site = Site.objects.get(pk=1); "
        "site.domain = '%s'; "
        "site.name = 'onepercentclub.com'; "
        "site.save()"
    ) % host

    with virtualenv():
        run_web('echo "%s" | ./manage.py shell --plain --settings=%s' % (
            sites_command, env.django_settings
        ))


@roles('dev')
@task
def deploy_dev(revspec='origin/master'):
    """
    Update the dev server to the specified revspec, or HEAD of deploy branch.
    """
    # Don't ask for confirmation
    env.noinput = True

    # Update git locally
    git_fetch_local()

    # Find commit for revspec
    commit = get_commit(revspec)

    # Make sure the remote git repo is up to date
    update_git(commit)

    # Get Django ready
    prepare_django()

    # Update site domain for self-reference to work
    set_site_domain()

    # Add the current git commit hash to the settings file
    add_git_commit()

    # Restart app server
    restart_site()


@roles('testing')
@task
def deploy_testing(revspec='origin/master'):
    """
    Update the testing server to the specified revspec, or HEAD of deploy branch and optionally sync migrated data.
    """
    # Update git locally
    git_fetch_local()

    # Find commit for revspec
    commit = get_commit(revspec)
    tag = find_available_tag('testing')

    # Make sure the remote git repo is up to date
    update_git(commit)

    # Get Django ready
    prepare_django()

    # Update site domain for self-reference to work
    set_site_domain()

    # Restart app server
    restart_site()

    # Deploy complete, tag commit
    tag_commit(commit.hexsha, tag)


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
    commit = get_commit(revspec)

    # Find latest available staging version
    tag = find_available_tag('staging')

    # Check whether this commit has been tested
    assert_release_tag(commit, 'testing')

    # Update the code
    update_tar(commit.hexsha)

    # Get Django ready
    prepare_django()

    # Update site domain for self-reference to work
    set_site_domain()

    # Restart app server
    restart_site()

    # Deploy complete, tag commit
    tag_commit(commit.hexsha, tag)


@roles('production')
@task
def deploy_production(revspec=None):
    """ Update the production server to the specified revspec, or the latest staging release. """

    # Update git locally
    git_fetch_local()

    # Find revspec or latest testing release
    if not revspec:
        version = find_latest_tag_version('staging')
        revspec = make_versioned_tag('staging', version)

    # Find commit for revspec
    commit = get_commit(revspec)

    # Find latest available staging version
    tag = find_available_tag('production')

    # Check whether this commit has been staged.
    assert_release_tag(commit, 'staging')

    # Update the code
    update_tar(commit.hexsha)

    # Get Django ready
    prepare_django()

    # Update site domain for self-reference to work
    set_site_domain()

    # Restart app server
    restart_site()

    # Deploy complete, tag commit
    tag_commit(commit.hexsha, tag)


@roles('backup')
@task
def get_db():
    backup_dir = "/home/backups/onepercentclub-backups/onepercentsite/current"
    with cd(backup_dir):
        output = run("ls *.bz2")
        try:
            filename = output.split()[0]
        except IndexError:
            print "No database backup file found"

        if filename:
            get(remote_path="{0}/{1}".format(backup_dir, filename), local_path="./dump.sql.bz2")
            unpack_db()

def unpack_db(filename="dump.sql.bz2"):
    try:
        local("gunzip {0}".format(filename))
    except IndexError:
        print "No database file found"

