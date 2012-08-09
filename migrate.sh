#!/bin/bash -ex

# First set resource limits to 1300MB max.
ulimit -v 1300000

# Drop database and remove existing files (allways succeed)
dropdb onepercentsite || true
rm -rf static/media || true

# Create new database
createdb -T template0 -E utf8 onepercentsite

# Manually take care of creating database (fixme in prepare.sh)
touch database.sqlite
bash prepare.sh

# Get into our environment
source env/bin/activate

# Set Django settings
export DJANGO_SETTINGS_MODULE=bluebottle.settings.testing

# Setup new database and start migration
python manage.py syncdb --noinput --migrate
python manage.py migrate_legacy -v 2

# Load fixtures
python manage.py loaddata project_category_data

# Dump database and archive media
pg_dump -x --no-owner onepercentsite | bzip2 -c > migrated_data.sql.bz2
tar cvf migrated_media.tar static/media
