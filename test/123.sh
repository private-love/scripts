#!/bin/bash
name=`echo $0|awk -F '/' '{print $NF}'`
echo $name
dir=`echo $0|awk -F $(echo $name) '{print $1}'`
echo $dir
