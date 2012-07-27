#!/bin/sh

sudo -u bluebottle dropdb bluebottle
sudo -u bluebottle createdb -T template0 -E utf8 bluebottle
bunzip2 -c /var/lib/jenkins/jobs/legacydb/lastSuccessful/archive/migrated_data.sql.bz2 | sudo -u bluebottle psql bluebottle
cd /var/www/bluebottle
sudo -u bluebottle tar xvf /var/lib/jenkins/jobs/legacydb/lastSuccessful/archive/migrated_media.tar
sudo -u bluebottle env/bin/python manage.py collectstatic --settings=bluebottle.settings.user_testing -l --noinput
sudo supervisorctl restart bluebottle

