#!/bin/sh

sudo -u bluebottle dropdb bluebottle_user_testing
sudo -u bluebottle createdb -T template0 -E utf8 bluebottle_user_testing
bunzip2 -c /var/lib/jenkins/jobs/legacydb/lastSuccessful/archive/migrated_data.sql.bz2 | sudo -u bluebottle psql bluebottle_user_testing
cd /var/www/bluebottle
sudo -u bluebottle tar xvf /var/lib/jenkins/jobs/legacydb/lastSuccessful/archive/migrated_media.tar
sudo -u onepercentadmin git pull
sudo -u onepercentadmin git merge origin/master
sudo -u onepercentadmin env/bin/pip install -r requirements.txt
#sudo -u bluebottle env/bin/python manage.py test
sudo -u bluebottle env/bin/python manage.py collectstatic --settings=bluebottle.settings.user_testing -l --noinput
sudo supervisorctl restart bluebottle

