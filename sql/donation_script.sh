
psql onepercentsite < donation_before_migrations.sql

./manage.py syncdb
./manage.py migrate orders 0001 --fake --delete-ghost-migrations
./manage.py migrate donations 0001 --fake

./manage.py migrate

psql onepercentsite < donation_after_migrations.sql
