#!/bin/sh
# Generate, compile, fetch and upload PO-files for the site

SOURCE_LANGUAGE="en"
MANAGE_PY="$PWD/manage.py"
MAKEMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE"
COMPILEMESSAGES="$MANAGE_PY compilemessages"
MINIMUM_PERC="80" # Don't pull in translations with less than this %

APPS="accounts donations geo media organizations projects"

case "$1" in
        generate)
            echo "Generating PO files"
            for APP in $APPS; do
                echo "Generating PO-file for $APP"
                APP_DIR="apps/$APP"
                (cd $APP_DIR && $MAKEMESSAGES)
            done

            echo "Generating PO-file for templates"
            mv locale templates/ && cd templates/ && $MAKEMESSAGES && mv locale ../

            ;;

        push)
            echo "Uploading PO files to Transifex"
            tx push -s

            ;;

        pull)
            echo "Fetching PO files from Transifex"
            tx pull -a --minimum-perc $MINIMUM_PERC

            ;;

        compile)
            echo "Compiling PO files"
            for APP in $APPS; do
                echo "Compiling PO-file for $APP"
                APP_DIR="apps/$APP"
                (cd $APP_DIR && $COMPILEMESSAGES)
            done

            echo "Generating PO-file for templates"
            $COMPILEMESSAGES

            ;;

        *)
            echo $"Usage: $0 {generate|push|pull|compile}"
            exit 1

esac
