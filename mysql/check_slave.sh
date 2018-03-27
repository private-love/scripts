#!/bin/sh
mysqlbin='/opt/ci123/mysql-5.6.25/bin/mysql'
#mysqllist=`ps aux|grep mysql|grep 'socket'|grep -v 'mysql3334.sock'|grep -v 'mysql3335.sock'|grep -v 'mysql3322.sock'|sed 's/ /:/g'|awk '{print $0}'`
mysqllist=`ps aux|grep mysql|grep 'socket'|grep -v 'mysql3306.sock'|sed 's/ /:/g'|awk '{print $0}'`
declare -a mysql_list
declare -a slave_is
for i in $mysqllist;do
for j in `echo $i|awk -F ':' '{ k=1;while(k<=NF){print $k;k++}}'`;do

if [ -n "${j}" ] && ([ `echo $j|grep 'datadir='` ] || [ `echo $j|grep 'socket='` ] || [ `echo $j|grep 'port='` ]);then
mysql_datastr=(`echo $j|awk -F "=" '{print $2}'`)
mysql_str=$mysql_str$mysql_datastr":"
if [ `echo $j|grep 'datadir='` ];then
mysql_datadir=(`echo $j|awk -F "=" '{print $2}'`)
elif [ `echo $j|grep 'socket='` ];then
mysql_socket=(`echo $j|awk -F "=" '{print $2}'`)
elif [ `echo $j|grep 'port='` ];then
mysql_port=(`echo $j|awk -F "=" '{print $2}'`)
fi
fi
done
mysql_str=""
dir=$mysql_port
sep=","
slave_is=($($mysqlbin  -S $mysql_socket -u root -p'hanfuboyuan0619'  -e "show slave status\G" 2>&1|grep Running |awk '{print $2}'))
if [ -n "${slave_is[0]}" ] || [ -n "${slave_is[1]}" ]
then
if [ "${slave_is[0]}" = "Yes" -a "${slave_is[1]}" = "Yes" ]
then
behind_master=($($mysqlbin  -S $mysql_socket -u root -p'hanfuboyuan0619'  -e "show slave status\G" --skip-secure-auth 2>&1 |grep Seconds_Behind_Master |awk '{print $2}'))
ok_str=$ok_str$dir$sep
behind_master_str=$behind_master_str$behind_master$sep
else
critical_str=$critical_str$dir$sep
fi
else
empty_str=$empty_str$dir$sep
fi
done

if [ -n "${ok_str}" ];then
let "ok_len=${#ok_str}-1"
let "behind_len=${#behind_master_str}-1"
echo_str="OK -{${ok_str:0:$ok_len}}slave is running,behind_master:{${behind_master_str:0:$behind_len}}"
fi
if [ -n "${critical_str}" ];then
let "cri_len=${#critical_str}-1"
echo_str=$echo_str"/Critical -{${critical_str:0:$cri_len}}slave is error"
critical_status="error"
fi
if [ -n "${empty_str}" ];then
let "emp_len=${#empty_str}-1"
echo_str=$echo_str"/Empty-{${empty_str:0:$emp_len}} slave is empty"
fi
echo ${echo_str}
if [ "$critical_status" == "error" ];then
exit 2;
else
exit 0;
fi
