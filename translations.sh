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

ROOT="$PWD"
APPS_ROOT="$PWD/apps"
BB_ROOT="$PWD/env-2.7/src/bluebottle/bluebottle"

MAKEMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE --no-wrap -e hbs,html,txt $SETTINGS"
MAKEJSMESSAGES="$MANAGE_PY makemessages -l $SOURCE_LANGUAGE --include=env-2.7/src/bluebottle/bluebottle --ignore=djangojs.js  --ignore=node_modules --no-wrap -e js -i compressed -d djangojs $SETTINGS"
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
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for projects"
            cd "$APPS_ROOT/projects"
            INCLUDES="--include=$BB_ROOT/bb_projects"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for fundraisers"
            cd "$APPS_ROOT/fundraisers"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for organizations"
            cd "$APPS_ROOT/organizations"
            INCLUDES="--include=$BB_ROOT/bb_organizations"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for tasks"
            cd "$APPS_ROOT/tasks"
            INCLUDES="--include=$BB_ROOT/bb_tasks"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for wallposts, partners, pages, news and homepage, and utils and common in BB"
            cd "$APPS_ROOT/homepage"
            INCLUDES=" --include=$ROOT/templates --include=$APPS_ROOT/core/ --include=$BB_ROOT/wallposts --include=$BB_ROOT/pages --include=$BB_ROOT/quotes --include=$BB_ROOT/slides --include=$BB_ROOT/contact --include=$BB_ROOT/news --include=$BB_ROOT/utils --include=$BB_ROOT/common --include=$APPS_ROOT/partners "
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-files for donations and payments"
            cd "$APPS_ROOT/donations"
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            INCLUDES="--include=$APPS_ROOT/fund --include=$APPS_ROOT/payouts --include=$APPS_ROOT/cowry --include=$APPS_ROOT/cowry_docdata --include=$APPS_ROOT/cowry_docdata_legacy"
            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/LC_MESSAGES/django.po
            $MANAGE_PY makemessages -l $SOURCE_LANGUAGE $INCLUDES --no-wrap -e hbs,html,txt $SETTINGS


            echo "Generating PO-file for javascripts"
            cd "$APPS_ROOT/.."

            # Make the locale dir if it's not there.
            if [ ! -d "locale" ]; then
                mkdir "locale"
            fi
            # Remove the old translations
            rm locale/en/djangojs.po
            $MAKEJSMESSAGES

            ;;

        push)
            echo "Uploading PO files to Transifex"
            tx push -s

            ;;

        pull)
            echo "Fetching PO files from Transifex"
            tx pull -a -f

            # Copy en_GB translations to en
            for APP_DIR in $APPS; do
                DIR="apps/$APP_DIR"
                cp $DIR/locale/en_GB/LC_MESSAGES/*.po $DIR/locale/en/LC_MESSAGES/
            done
            echo "Overwriting en translations with en_GB for JS code"
            cp locale/en_GB/LC_MESSAGES/*.po locale/en/LC_MESSAGES/
            ;;

        compile)
            echo "Compiling PO files"
            for APP_DIR in $APPS; do
                DIR="apps/$APP_DIR"
                echo "Compiling PO-file for $DIR"
                (cd $DIR && $COMPILEMESSAGES)
            done

            echo "Generating PO-file for javascript"
            $COMPILEMESSAGES
            $COMPILEJSMESSAGES

            ;;

        *)
            echo $"Usage: $0 {generate|push|pull|compile}"
            exit 1
esac
