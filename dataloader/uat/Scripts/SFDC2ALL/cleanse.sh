#!/bin/sh
shdir=$( cd "$( dirname "$0" )" && pwd )

rm -f $shdir/export_Organizations/read/*.csv
rm -f $shdir/export_Organizations/write/*.csv
rm -f $shdir/export_Organizations/log/*.csv
cp /dev/null $shdir/export_Organizations/log/sdl.log
rm -f $shdir/export_Users/read/*.csv
rm -f $shdir/export_Users/write/*.csv
rm -f $shdir/export_Users/log/*.csv
cp /dev/null $shdir/export_Users/log/sdl.log
rm -f $shdir/export_Projects/read/*.csv
rm -f $shdir/export_Projects/write/*.csv
rm -f $shdir/export_Projects/log/*.csv
cp /dev/null $shdir/export_Projects/log/sdl.log
rm -f $shdir/export_Projectbudgetlines/read/*.csv
rm -f $shdir/export_Projectbudgetlines/write/*.csv
rm -f $shdir/export_Projectbudgetlines/log/*.csv
cp /dev/null $shdir/export_Projectbudgetlines/log/sdl.log
rm -f $shdir/export_Donations/read/*.csv
rm -f $shdir/export_Donations/write/*.csv
rm -f $shdir/export_Donations/log/*.csv
cp /dev/null $shdir/export_Donations/log/sdl.log
rm -f $shdir/export_Tasks/read/*.csv
rm -f $shdir/export_Tasks/write/*.csv
rm -f $shdir/export_Tasks/log/*.csv
cp /dev/null $shdir/export_Tasks/log/sdl.log
rm -f $shdir/export_Taskmembers/read/*.csv
rm -f $shdir/export_Taskmembers/write/*.csv
rm -f $shdir/export_Taskmembers/log/*.csv
cp /dev/null $shdir/export_Taskmembers/log/sdl.log
rm -f $shdir/export_Vouchers/read/*.csv
rm -f $shdir/export_Vouchers/write/*.csv
rm -f $shdir/export_Vouchers/log/*.csv
cp /dev/null $shdir/export_Vouchers/log/sdl.log