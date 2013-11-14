#!/bin/sh
# Generate, compile, fetch and upload PO-files for the site

SOURCE_LANGUAGE="en"
MANAGE_PY="$PWD/manage.py"
SETTINGS=""
if [ $2 ]; then
    SETTINGS="--settings=$2"
fi
MAKEMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE --no-wrap -e hbs,html,txt $SETTINGS"
MAKEJSMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE --no-wrap -e js -i compressed -d djangojs $SETTINGS"
COMPILEMESSAGES="$MANAGE_PY compilemessages $SETTINGS"
COMPILEJSMESSAGES="$MANAGE_PY compilejsi18n $SETTINGS"
APPS_DIR="apps"
EXCLUDED_APPS=""

APPS=""
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


# APPS="accounts fund geo organizations projects wallposts reactions homepage"

case "$1" in
        generate)
            echo "Generating PO files"
            for APP_DIR in $APPS; do
                echo "Generating PO-file for $APP_DIR"
                (cd $APP_DIR && $MAKEMESSAGES)
            done

            echo "Generating PO-file for templates"
            mv locale templates/ && cd templates/ && $MAKEMESSAGES
            echo "Generating PO-file for javascripts"
            $MAKEJSMESSAGES

            mv locale ../

            ;;

        push)
            echo "Uploading PO files to Transifex"
            tx push -s

            ;;

        pull)
            echo "Fetching PO files from Transifex"
            tx pull -l nl

            ;;

        compile)
            echo "Compiling PO files"
            for APP_DIR in $APPS; do
                echo "Compiling PO-file for $APP_DIR"
                (cd $APP_DIR && $COMPILEMESSAGES)


            done

            echo "Generating PO-file for templates"
            $COMPILEMESSAGES
            echo "Generating PO-file for javascript"
            $COMPILEJSMESSAGES

            ;;

        *)
            echo $"Usage: $0 {generate|push|pull|compile}"
            exit 1
esac
