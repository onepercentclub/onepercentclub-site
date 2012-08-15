#!/bin/sh

# Go to current directory
cd `dirname $0`

PWD=`pwd`
BASEPATH=`basename $PWD`

GIT=git
VIRTUALENV="virtualenv --system-site-packages --distribute --prompt=($BASEPATH)"
PIP="pip --timeout 30 -q"
ENVDIR=env

SETTINGS_DIR=$PWD/bluebottle/settings
MANAGE_PY="$ENVDIR/bin/python ./manage.py"

echo "Checking PIP and virtualenv availability"
pip install 'pip>=1.0' 'virtualenv>=1.7.1.2'

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
fi

echo 'Installing required packages'
# Install Django first because django-countries requires Django to be fully
# installed before it will install.
DJANGO=`grep "Django==" requirements.txt`
$ENVDIR/bin/pip install $DJANGO
if [ $? -ne 0 ]; then
    echo "Error installing $DJANGO."
    exit 1
fi
if $ENVDIR/bin/pip install -r requirements.txt; then
    echo 'That went allright, continue'
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
if [ ! -f $SECRETS_FILE ]; then
    echo
    echo "Generating secret key in $SECRETS_FILE"
    # The generate_secret_key command produces a superfluous warning message
    # that needs to be removed by filtering out only the last line of the
    # output.
    SECRET_KEY=`$MANAGE_PY generate_secret_key | tail -1`

    if [ $SECRET_KEY  ]; then
        echo "# Add passwords passwords and other secrets data in this file" >> $SECRETS_FILE
        echo >> $SECRETS_FILE
        echo "# Make this unique, and don't share it with anybody." >> $SECRETS_FILE
        echo "SECRET_KEY = '$SECRET_KEY'" >> $SECRETS_FILE
        echo >> $SECRETS_FILE
    else
        echo 'Error generating secret key, breaking off.'
        exit 1
    fi
fi

echo "Please configure your local database in $SECRETS_FILE and run './manage.py syncdb --migrate to get you started.'"
