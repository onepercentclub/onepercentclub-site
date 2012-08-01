#!/bin/sh -ex

# First set resource limits
ulimit -v 500000

# Drop database and remove existing files (allways succeed)
echo 'DROP DATABASE onepercentsite' | psql onepercentsite
rm -rf static/media

# Create new database
createdb -T template0 -E utf8 onepercentsite

# Manually take care of creating database (fixme in prepare.sh)
touch database.sqlite
bash prepare.sh

# Get into our environment
. env/bin/activate

# Setup new database and start migration
python manage.py syncdb --noinput --migrate --settings=bluebottle.settings.testing
python manage.py migrate_legacy -v 2 

# Load fixtures
python manage.py --settings=bluebottle.settings.testing
python manage.py loaddata project_category_data

# Dump database and archive media
pg_dump -x onepercentsite | bzip2 -c > migrated_data.sql.bz2
tar cvf migrated_media.tar static/media
