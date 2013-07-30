#!/bin/sh
shdir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
shdirname=$( echo $shdir | sed 's!.*/!!' )
cd $shdir
java -cp $shdir/../../../Bin/DataLoader20/DataLoader.jar -Dsalesforce.config.dir=$shdir/config com.salesforce.dataloader.process.ProcessRunner process.name=$shdirname
