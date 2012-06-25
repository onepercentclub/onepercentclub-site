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
pip install 'pip>=1.1' 'virtualenv>=1.7.1.2'
if [ $? == 0 ]; then
    echo 'PIP and virtualenv installed allright'
else
    echo 'Error installing PIP and virtualenv, breaking off'
    echo 'Please execute the following command manually, and watch for errors:'
    echo "    pip install 'pip>=1.1' 'virtualenv>=1.7.1.2'"
    exit 1
fi


if [ ! -d $ENVDIR ]; then
    echo "Preparing virtualenv environment in $ENVDIR directory"
    $VIRTUALENV $ENVDIR
fi

echo 'Installing required packages'
if $ENVDIR/bin/pip install -r requirements.txt; then
    echo 'That went allright, continue'
else
    echo 'Error installing dependencies, breaking off'
    exit 1
fi

if [ ! -f $SETTINGS_DIR/local.py ]; then
    echo 'No local settings file found.'
    cp -v $SETTINGS_DIR/local.py.example $SETTINGS_DIR/local.py
fi

if [ ! -f $SETTINGS_DIR/secret.py ]; then
    echo
    echo 'Generating secret key in settings_secret.py.'
    SECRET_KEY=`$MANAGE_PY generate_secret_key`

    echo "# Add passwords passwords and other secrets data in this file" >> $SETTINGS_DIR/secret.py
    echo >> $SETTINGS_DIR/secret.py
    echo "# Make this unique, and don't share it with anybody." >> $SETTINGS_DIR/secret.py
    echo "SECRET_KEY = '$SECRET_KEY'" >> $SETTINGS_DIR/secret.py
    echo >> $SETTINGS_DIR/secret.py
fi

if [ ! -f database.sqlite ]; then
    echo 'No database found, running syncdb and migrate.'
    $MANAGE_PY syncdb
    $MANAGE_PY migrate
fi
