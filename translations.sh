#!/bin/sh
# Generate, compile, fetch and upload PO-files for the site

SOURCE_LANGUAGE="en"
MANAGE_PY="$PWD/manage.py"
MAKEMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE -e hbs -e html"
COMPILEMESSAGES="$MANAGE_PY compilemessages"
MINIMUM_PERC="80" # Don't pull in translations with less than this %
APPS_DIR="../apps"
EXCLUDED_APPS=""

APPS=""
cd bluebottle
for dir in $(find $APPS_DIR -maxdepth 1 -type d); do
    if [ $dir = $APPS_DIR ]; then
        continue
    fi
    app=$(echo $dir | sed -e "s|$APPS_DIR/||")
    echo $EXCLUDED_APPS | grep -q $app
    if [ $? -eq 0 ]; then
        # $app is in $EXCLUDED_APPS list.
        continue
    fi

    APPS="$APPS $dir"

    # Make the locale dir if it's not there.
    if [ ! -d "$dir/locale" ]; then
        mkdir "$dir/locale"
    fi
done

#APPS="accounts fund geo organizations projects wallposts reactions"

case "$1" in
        generate)
            echo "Generating PO files"
            for APP_DIR in $APPS; do
                echo "Generating PO-file for $APP_DIR"
                (cd $APP_DIR && $MAKEMESSAGES)
            done

            echo "Generating PO-file for templates"
            mv locale templates/ && cd templates/ && $MAKEMESSAGES
            mv locale ../

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
            for APP_DIR in $APPS; do
                echo "Compiling PO-file for $APP_DIR"
                (cd $APP_DIR && $COMPILEMESSAGES)
            done

            echo "Generating PO-file for templates"
            $COMPILEMESSAGES

            ;;

        *)
            echo $"Usage: $0 {generate|push|pull|compile}"
            exit 1
esac
