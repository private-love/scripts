#!/bin/bash
while true
do
    [ -f ./.lock ] && sleep 10 || break
done
touch .lock
echo $1
sleep 20
name=`echo $0|awk -F '/' '{print $NF}'`
echo $name
dir=`echo $0|awk -F $(echo $name) '{print $1}'`
echo $dir
/bin/rm -f .lock
