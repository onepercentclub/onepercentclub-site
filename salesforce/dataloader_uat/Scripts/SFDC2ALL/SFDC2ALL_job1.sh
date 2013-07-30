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

echo "Exporting data from Salesforce..."

sleep 3
echo "Processing Organizations"
source $scriptdir/export_Organizations/export_Organizations.sh

sleep 3
echo "Processing Users"
source $scriptdir/export_Users/export_Users.sh

sleep 3
echo "Processing Projects"
source $scriptdir/export_Projects/export_Projects.sh

sleep 3
echo "Processing Projectbudgetlines"
source $scriptdir/export_Projectbudgetlines/export_Projectbudgetlines.sh

sleep 3
echo "Processing Donations"
source $scriptdir/export_Donations/export_Donations.sh

sleep 3
echo "Processing Vouchers"
source $scriptdir/export_Vouchers/export_Vouchers.sh

sleep 3
echo "Processing Tasks"
source $scriptdir/export_Tasks/export_Tasks.sh

sleep 3
echo "Processing Taskmembers"
source $scriptdir/export_Taskmembers/export_Taskmembers.sh

sleep 3

echo "Moving output CSV files to output directories..."
mv -f $scriptdir/export_Organizations/write/export_Organizations.csv $scriptdir/../../Data/Output/SFDC2ALL_Organizations_$date_now.csv
mv -f $scriptdir/export_Users/write/export_Users.csv $scriptdir/../../Data/Output/SFDC2ALL_Users_$date_now.csv
mv -f $scriptdir/export_Projects/write/export_Projects.csv $scriptdir/../../Data/Output/SFDC2ALL_Projects_$date_now.csv
mv -f $scriptdir/export_Projectbudgetlines/write/export_Projectbudgetlines.csv $scriptdir/../../Data/Output/SFDC2ALL_Projectbudgetlines_$date_now.csv
mv -f $scriptdir/export_Donations/write/export_Donations.csv $scriptdir/../../Data/Output/SFDC2ALL_Donations_$date_now.csv
mv -f $scriptdir/export_Vouchers/write/export_Vouchers.csv $scriptdir/../../Data/Output/SFDC2ALL_Vouchers_$date_now.csv
mv -f $scriptdir/export_Tasks/write/export_Tasks.csv $scriptdir/../../Data/Output/SFDC2ALL_Tasks_$date_now.csv
mv -f $scriptdir/export_Taskmembers/write/export_Taskmembers.csv $scriptdir/../../Data/Output/SFDC2ALL_Taskmembers_$date_now.csv


echo "Archiving logs and input/ouput..."
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Organizations.tgz $scriptdir/export_Organizations/read $scriptdir/export_Organizations/write $scriptdir/export_Organizations/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Users.tgz $scriptdir/export_Users/read $scriptdir/export_Users/write $scriptdir/export_Users/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Projects.tgz $scriptdir/export_Projects/read $scriptdir/export_Projects/write $scriptdir/export_Projects/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Projectbudgetlines.tgz $scriptdir/export_Projectbudgetlines/read $scriptdir/export_Projectbudgetlines/write $scriptdir/export_Projectbudgetlines/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Donations.tgz $scriptdir/export_Donations/read $scriptdir/export_Donations/write $scriptdir/export_Donations/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Vouchers.tgz $scriptdir/export_Vouchers/read $scriptdir/export_Vouchers/write $scriptdir/export_Vouchers/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Tasks.tgz $scriptdir/export_Tasks/read $scriptdir/export_Tasks/write $scriptdir/export_Tasks/log
tar -czvpf $scriptdir/archive/$date_now-$time_now-SFDC2ALL_export_Taskmembers.tgz $scriptdir/export_Taskmembers/read $scriptdir/export_Taskmembers/write $scriptdir/export_Taskmembers/log

echo "Finished successfully!"
cd $scriptdir
exit 0
