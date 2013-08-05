#!/bin/sh
shdir=$( cd "$( dirname "$0" )" && pwd )

rm -f $shdir/upsert_Organizations/read/*.csv
rm -f $shdir/upsert_Organizations/write/*.csv
rm -f $shdir/upsert_Organizations/log/*.csv
rm -f $shdir/upsert_Organizations/log/*lastRun.properties
cp /dev/null $shdir/upsert_Organizations/log/sdl.log
rm -f $shdir/upsert_Users/read/*.csv
rm -f $shdir/upsert_Users/write/*.csv
rm -f $shdir/upsert_Users/log/*.csv
rm -f $shdir/upsert_Users/log/*lastRun.properties
cp /dev/null $shdir/upsert_Users/log/sdl.log
rm -f $shdir/upsert_Projects/read/*.csv
rm -f $shdir/upsert_Projects/write/*.csv
rm -f $shdir/upsert_Projects/log/*.csv
rm -f $shdir/upsert_Projects/log/*lastRun.properties
cp /dev/null $shdir/upsert_Projects/log/sdl.log
rm -f $shdir/upsert_Projectbudgetlines/read/*.csv
rm -f $shdir/upsert_Projectbudgetlines/write/*.csv
rm -f $shdir/upsert_Projectbudgetlines/log/*.csv
rm -f $shdir/upsert_Projectbudgetlines/log/*lastRun.properties
cp /dev/null $shdir/upsert_Projectbudgetlines/log/sdl.log
rm -f $shdir/upsert_Donations/read/*.csv
rm -f $shdir/upsert_Donations/write/*.csv
rm -f $shdir/upsert_Donations/log/*.csv
rm -f $shdir/upsert_Donations/log/*lastRun.properties
cp /dev/null $shdir/upsert_Donations/log/sdl.log
rm -f $shdir/upsert_Tasks/read/*.csv
rm -f $shdir/upsert_Tasks/write/*.csv
rm -f $shdir/upsert_Tasks/log/*.csv
rm -f $shdir/upsert_Tasks/log/*lastRun.properties
cp /dev/null $shdir/upsert_Tasks/log/sdl.log
rm -f $shdir/upsert_Taskmembers/read/*.csv
rm -f $shdir/upsert_Taskmembers/write/*.csv
rm -f $shdir/upsert_Taskmembers/log/*.csv
rm -f $shdir/upsert_Taskmembers/log/*lastRun.properties
cp /dev/null $shdir/upsert_Taskmembers/log/sdl.log
