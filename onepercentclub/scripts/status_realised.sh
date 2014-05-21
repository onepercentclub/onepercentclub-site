#!/bin/bash
source ../../env/bin/activate
python ./manage.py cron_status_realised --settings=onepercentclub.settings.$1