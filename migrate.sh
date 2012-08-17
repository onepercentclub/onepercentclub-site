#!/bin/bash -ex

DB_NAME=onepercentsite_migration

# First set resource limits to 1300MB max.
ulimit -v 1300000

# Drop database and remove existing files (allways succeed)
dropdb $DB_NAME || true
rm -rf static/media || true

# Create new database
createdb -T template0 -E utf8 $DB_NAME

# Setup datastructure and project
bash prepare.sh

# Get into our environment
source env/bin/activate

# Set Django settings
export DJANGO_SETTINGS_MODULE=bluebottle.settings.migration

# Setup new database
python manage.py syncdb --noinput --migrate

# The fixtures for geo app are needed for the migration to work.
python manage.py loaddata region_subregion_country_dump

# Do the migration.
python manage.py migrate_legacy -v 2

# Load fixtures for the project categories.
python manage.py loaddata project_category_data

# Dump database and archive media
pg_dump -x --no-owner $DB_NAME | bzip2 -c > migrated_data.sql.bz2
tar cvf migrated_media.tar static/media
