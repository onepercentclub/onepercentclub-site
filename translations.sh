#!/bin/sh
# Generate, compile, fetch and upload PO-files for the site

SOURCE_LANGUAGE="en"

SETTINGS=""
if [ $2 ]; then
    SETTINGS="--settings=$2"
fi

MANAGE_PY="manage.py"
PROJECT_DIR="$PWD"

MAKEMESSAGES="python $MANAGE_PY makemessages -s --include=apps --include=env/src/bluebottle --no-wrap -e html,txt,hbs --no-obsolete $SETTINGS"
MAKEJSMESSAGES="python $MANAGE_PY makemessages --include=apps --include=./env/src/bluebottle --no-wrap -e js --ignore=compressed --ignore=djangojs.js -d djangojs --no-obsolete $SETTINGS"
COMPILEMESSAGES="python $MANAGE_PY compilemessages $SETTINGS"
COMPILEJSMESSAGES="python $MANAGE_PY compilejsi18n -o $PROJECT_DIR/core/static/jsi18n $SETTINGS"

case "$1" in
        generate)
            echo "Generating PO files for templates"
            (cd $PROJECT_DIR && $MAKEMESSAGES)

            echo "Generating PO-file for javascripts"
            (cd $PROJECT_DIR && $MAKEJSMESSAGES)

            ;;

        push)
            echo "Uploading PO files to Transifex"
            tx push -s

            ;;

        pull)
            echo "Fetching PO files from Transifex"
            tx pull --all

            # Workaround for translating (generic) English.
            cp $PROJECT_DIR/locale/en_GB/LC_MESSAGES/*.po $PROJECT_DIR/locale/en/LC_MESSAGES/

            ;;

        compile)
            echo "Compiling PO-file for templates"
            (cd $PROJECT_DIR && $COMPILEMESSAGES)

            echo "Compiling PO-file for javascript"
            (cd $PROJECT_DIR && $COMPILEJSMESSAGES)

            ;;

        *)

            echo $"Usage: $0 {generate|push|pull|compile}"
            exit 1
esac
