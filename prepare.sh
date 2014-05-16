#!/bin/sh -u

# Go to current directory
cd `dirname $0`

PWD=`pwd`
BASEPATH=`basename $PWD`

GIT=git
VIRTUALENV="virtualenv --system-site-packages --distribute --prompt=($BASEPATH)"
PIP="pip --timeout 30 -q --use-mirrors"
ENVDIR=env

SETTINGS_DIR=$PWD/onepercentclub/settings
MANAGE_PY="$ENVDIR/bin/python ./manage.py"

echo "Checking PIP and virtualenv availability"
#pip install 'pip>=1.0' 'virtualenv>=1.7.1.2'

if [ $? -eq 0 ]; then
    echo 'PIP and virtualenv available'
else
    echo 'Error installing PIP and virtualenv, breaking off.'
    echo 'Please install PIP >= 1.0 and VirtualEnv >= 1.7.1.2 manually.'
    exit 1
fi

if [ ! -d $ENVDIR ]; then
    echo "Preparing virtualenv environment in $ENVDIR directory"
    $VIRTUALENV $ENVDIR
    $ENVDIR/bin/pip install --upgrade setuptools
fi

echo 'Installing required packages'

# Install Django first because some Django apps require Django to be fully
# installed before they will install properly.
DJANGO=`grep "Django==" requirements/requirements.txt`
$ENVDIR/bin/pip install $DJANGO
if [ $? -ne 0 ]; then
    echo "Error installing $DJANGO."
    exit 1
fi
if $ENVDIR/bin/pip install -r requirements/requirements.txt; then
    echo 'That went alright, continue'
else
    echo 'Error installing dependencies, breaking off'
    exit 1
fi

LOCAL_SETTINGS=$SETTINGS_DIR/local.py
LOCAL_SETTINGS_EXAMPLE=$SETTINGS_DIR/local.py.example
if [ ! -f $LOCAL_SETTINGS ]; then
    echo "No local settings file found, copying from $LOCAL_SETTINGS_EXAMPLE"
    cp -v $LOCAL_SETTINGS_EXAMPLE $LOCAL_SETTINGS
fi

SECRETS_FILE=$SETTINGS_DIR/secrets.py
SECRETS_FILE_EXAMPLE=$SETTINGS_DIR/secrets.py.example
if [ ! -f $SECRETS_FILE ]; then
    echo
    echo "No secrets file found, copying from $SECRETS_FILE_EXAMPLE"
    cp -v $SECRETS_FILE_EXAMPLE $SECRETS_FILE

    echo "Generating secret key"
    # Ref: https://build.opensuse.org/package/view_file?file=fix-initscript.dif&package=cobbler&project=systemsmanagement
    RAND_SECRET=$(openssl rand -base64 42 | sed 's/\//\\\//g')

    if [ $RAND_SECRET  ]; then
        # Update SECRET_KEY
        sed -i "s/^SECRET_KEY.*/SECRET_KEY = \'$RAND_SECRET\'/" $SECRETS_FILE
    else
        echo 'Error generating secret key, breaking off.'

        # Cleanup after ourselves
        rm -f $SECRETS_FILE
        exit 1
    fi
fi

echo "Please configure your local database in $SECRETS_FILE and run './manage.py syncdb --migrate to get you started.'"
