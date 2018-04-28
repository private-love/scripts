#!/bin/bash
database=ipv4_2
function check () {
for((i=2;i<=254;i++))
do
 {
 ip=192.168.2.$i
 arp123=`arping -I eth0 -f -w 1 $ip|grep Unicast|awk '{print $5}'|awk -F '[' '{print $2}'|awk -F ']' '{print $1}'`
 if [[ "$arp123" != "" ]]
  then macs=`mysql -h192.168.0.238 -uipcheck -p'fuyuan1906' -e "use ip;select mac from $database where id=$i;"`
       mac=`echo $macs|awk '{print $2}'`
       if [[ "$mac" != "arp123" ]]
       then mysql -h192.168.0.238 -uipcheck -p'fuyuan1906' -e "use ip;update $database set mac='$arp123' where id=$i;"
		    mysql -h192.168.0.238 -uipcheck -p'fuyuan1906' -e "use ip;update $database set date=$(date +%s) where id=$i;"
       fi
 fi
 }&
done
wait
}
check
