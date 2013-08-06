#!/bin/bash
curdir=$(pwd)
scriptdir=$( cd "$( dirname "$0" )" && pwd )
scriptdirname=$( echo $scriptdir | sed 's!.*/!!' )
date_now=$( date +%Y%m%d )
time_now=$( date +%H%M )
progname=$(basename $0)

function error_exit
{
  echo "[ERROR] ${progname}: ${1:-"Unknown Error"}" 1>&2
  cd $scriptdir
  exit 1
}

echo "Cleansing log, input and output directories..."
source $scriptdir/cleanse.sh

echo "Moving input CSV files to read directories..."
if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Organizations_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Organizations_$date_now.csv $scriptdir/upsert_Organizations/read/upsert_Organizations.csv
else
  error_exit "File "BLUE2SFDC_Organizations_$date_now.csv" not found"
fi

if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Users_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Users_$date_now.csv $scriptdir/upsert_Users/read/upsert_Users.csv
else
  error_exit "File "BLUE2SFDC_Users_$date_now.csv" not found"
fi

if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Projects_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Projects_$date_now.csv $scriptdir/upsert_Projects/read/upsert_Projects.csv
else
  error_exit "File "BLUE2SFDC_Projects_$date_now.csv" not found"
fi

if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Projectbudgetlines_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Projectbudgetlines_$date_now.csv $scriptdir/upsert_Projectbudgetlines/read/upsert_Projectbudgetlines.csv
else
  error_exit "File "BLUE2SFDC_Projectbudgetlines_$date_now.csv" not found"
fi

if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Donations_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Donations_$date_now.csv $scriptdir/upsert_Donations/read/upsert_Donations.csv
else
  error_exit "File "BLUE2SFDC_Donations_$date_now.csv" not found"
fi

if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Tasks_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Tasks_$date_now.csv $scriptdir/upsert_Tasks/read/upsert_Tasks.csv
else
  error_exit "File "BLUE2SFDC_Tasks_$date_now.csv" not found"
fi

if [ -e $scriptdir/../../Data/Input/BLUE2SFDC_Taskmembers_$date_now.csv ];
then
  mv -f $scriptdir/../../Data/Input/BLUE2SFDC_Taskmembers_$date_now.csv $scriptdir/upsert_Taskmembers/read/upsert_Taskmembers.csv
else
  error_exit "File "BLUE2SFDC_Taskmembers_$date_now.csv" not found"
fi


echo "Uploading input data to Salesforce..."

sleep 3
echo "Processing Organizations"
source $scriptdir/upsert_Organizations/upsert_Organizations.sh

sleep 3
echo "Processing Users"
source $scriptdir/upsert_Users/upsert_Users.sh

sleep 3
echo "Processing Projects"
source $scriptdir/upsert_Projects/upsert_Projects.sh

sleep 3
echo "Processing Projectbudgetlines"
source $scriptdir/upsert_Projectbudgetlines/upsert_Projectbudgetlines.sh

sleep 3
echo "Processing Donations"
source $scriptdir/upsert_Donations/upsert_Donations.sh

sleep 3
echo "Processing Tasks"
source $scriptdir/upsert_Tasks/upsert_Tasks.sh

sleep 3
echo "Processing Taskmembers"
source $scriptdir/upsert_Taskmembers/upsert_Taskmembers.sh

sleep 3

echo "Archiving logs and input/ouput..."
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Organizations.tgz $scriptdir/upsert_Organizations/read $scriptdir/upsert_Organizations/write $scriptdir/upsert_Organizations/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Users.tgz $scriptdir/upsert_Users/read $scriptdir/upsert_Users/write $scriptdir/upsert_Users/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Projects.tgz $scriptdir/upsert_Projects/read $scriptdir/upsert_Projects/write $scriptdir/upsert_Projects/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Projectbudgetlines.tgz $scriptdir/upsert_Projectbudgetlines/read $scriptdir/upsert_Projectbudgetlines/write $scriptdir/upsert_Projectbudgetlines/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Donations.tgz $scriptdir/upsert_Donations/read $scriptdir/upsert_Donations/write $scriptdir/upsert_Donations/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Tasks.tgz $scriptdir/upsert_Tasks/read $scriptdir/upsert_Tasks/write $scriptdir/upsert_Tasks/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-BLUE2SFDC_upsert_Taskmembers.tgz $scriptdir/upsert_Taskmembers/read $scriptdir/upsert_Taskmembers/write $scriptdir/upsert_Taskmembers/log

echo "Finished successfully!"
cd $scriptdir
exit 0
