#!/bin/sh

# Refresh the database
sudo -u bluebottle dropdb bluebottle_user_testing
sudo -u bluebottle createdb -T template0 -E utf8 bluebottle_user_testing

# Load the latest succesful migration into the database
bunzip2 -c /var/lib/jenkins/jobs/legacydb/lastSuccessful/archive/migrated_data.sql.bz2 | sudo -u bluebottle psql bluebottle_user_testing

# Go to bluebottle folder
cd /var/www/bluebottle

# Make migrated files available
sudo -u bluebottle tar xvf /var/lib/jenkins/jobs/legacydb/lastSuccessful/archive/migrated_media.tar

# Update the source repo
sudo -u onepercentadmin git pull
sudo -u onepercentadmin git merge origin/master

# Let the remote peeps know where we at
sudo -u onepercentadmin git push origin testing

# Update Python requirements
sudo -u onepercentadmin env/bin/pip install -r requirements.txt

# Run unittests
#sudo -u bluebottle env/bin/python manage.py test

# Collect static files
sudo -u bluebottle env/bin/python manage.py collectstatic --settings=bluebottle.settings.user_testing -l --noinput

# Restart the bluebottle app server
sudo supervisorctl restart bluebottle
