#!/bin/sh
# Generate, compile, fetch and upload PO-files for the site

# Generate will create PO files.
# It wil run through some modules that will group some apps together
# e.g. Members:
#    echo "Generating PO-files for members"
#    cd "$APPS_ROOT/members"
#    INCLUDES="--include=$BB_ROOT/bb_accounts"
# It will cd to apps/members and then generate PO file including strings for bb_accounts



SOURCE_LANGUAGE="en"
MANAGE_PY="$PWD/manage.py"
SETTINGS=""
if [ $2 ]; then
    SETTINGS="--settings=$2"
fi

APPS_ROOT="$PWD/apps"
BB_ROOT="$PWD/env/src/bluebottle/bluebottle"

MAKEMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE --no-wrap -e hbs,html,txt $SETTINGS"
MAKEJSMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE --include=../../apps --include=../../env/src/bluebottle/bluebottle --ignore=djangojs.js --no-wrap -e js -i compressed -d djangojs $SETTINGS"
COMPILEMESSAGES="$MANAGE_PY compilemessages $SETTINGS"
COMPILEJSMESSAGES="$MANAGE_PY compilejsi18n $SETTINGS"
APPS_DIR="apps"

# All apps that hold translations. This is used by `pull` and `compile`.
APPS="projects members fundraisers organizations tasks homepage donations"

case "$1" in
        generate)
            echo "Let's create some PO-files!"

            echo "Generating PO-files for members"
            cd "$APPS_ROOT/members"
            INCLUDES="--include=$BB_ROOT/bb_accounts"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for projects"
            cd "$APPS_ROOT/projects"
            INCLUDES="--include=$BB_ROOT/bb_projects"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for fundraisers"
            cd "$APPS_ROOT/fundraisers"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for organizations"
            cd "$APPS_ROOT/organizations"
            INCLUDES="--include=$BB_ROOT/bb_organizations"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for tasks"
            cd "$APPS_ROOT/tasks"
            INCLUDES="--include=$BB_ROOT/bb_tasks"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for wallposts, pages, news and homepage"
            cd "$APPS_ROOT/homepage"
            INCLUDES="--include=$APPS_ROOT/core/ --include=$BB_ROOT/wallposts --include=$BB_ROOT/pages --include=$BB_ROOT/quotes --include=$BB_ROOT/slides --include=$BB_ROOT/contact --include=$BB_ROOT/news"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for donations and payments"
            cd "$APPS_ROOT/donations"
            INCLUDES="--include=$APPS_ROOT/fund --include=$APPS_ROOT/payouts --include=$APPS_ROOT/cowry --include=$APPS_ROOT/cowry_docdata --include=$APPS_ROOT/cowry_docdata_legacy"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-file for javascripts"
            cd "$APPS_ROOT/core"

            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            $MAKEJSMESSAGES

            ;;

        push)
            echo "Uploading PO files to Transifex"
            tx push -s

            ;;

        pull)
            echo "Fetching PO files from Transifex"
            tx pull -a

            # Copy en_GB translations to en
            for APP_DIR in $APPS; do
                DIR="apps/$APP_DIR"
                cp $DIR/locale/en_GB/LC_MESSAGES/*.po $DIR/locale/en/LC_MESSAGES/
            done
            ;;

        compile)
            echo "Compiling PO files"
            for APP_DIR in $APPS; do
                DIR="apps/$APP_DIR"
                echo "Compiling PO-file for $DIR"
                (cd $DIR && $COMPILEMESSAGES)
            done

            echo "Generating PO-file for javascript"
            $COMPILEJSMESSAGES

            ;;

        *)
            echo $"Usage: $0 {generate|push|pull|compile}"
            exit 1
esac
