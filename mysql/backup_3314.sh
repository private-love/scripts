#!/bin/sh
LogFile=db$(date +%y%m%d).log
week=`date +%w`
cd /opt/ci123/backup/3314
for DBName in 3314
do
#NewFile=db$DBName$(date +%y%m%d).tar.gz
NewFile=db$DBName$(date +%y%m%d).sql.gz
OldLogFile=db$(date -d '7 days ago' +%y%m%d).log
if [ -f $OldLogFile ]
then
        rm -f $OldLogFile >> $LogFile 2>&1
        echo "[$OldLogFile]Delete Old log File Success!" >> $LogFile
else
        echo "[$OldLogFile]No Old log File!" >> $LogFile
fi

case $week in
        1)
                date=`date -d '56 days ago' +%y%m%d`
                OldFile=db$DBName$date.sql.gz
                if [ -f $OldFile ]
                then
                        rm -f $OldFile >> $LogFile 2>&1
                        echo "[$OldFile]Delete Old File Success!" >> $LogFile
                else
                        echo "[$OldFile]No Old Backup File!" >> $LogFile
                fi
        ;;
        2|3|4|5|6|0)
                date=`date -d '7 days ago' +%y%m%d`
                OldFile=db$DBName$date.tar.gz
                if [ -f $OldFile ]
                then
                        rm -f $OldFile >> $LogFile 2>&1
                        echo "[$OldFile]Delete Old File Success!" >> $LogFile
                else
                        echo "[$OldFile]No Old Backup File!" >> $LogFile
                fi
        ;;
esac
if [ -f $NewFile ]
then
   echo "[$NewFile]The Backup File is exists,Can't Backup!" >> $LogFile
else
      datestart=$(date +%s)
#      if [ -z $DBPasswd ]
#      then
#         mysqldump -u $DBUser --opt $DBName |gzip > $NewFile
#      else
        echo "start backup" >> $LogFile
        cd /opt/ci123/data/yuanliang_3314
        /opt/ci123/mysql-5.6.25/bin/mysql -S /tmp/mysql3314.sock -p'hanfuboyuan0619' -e "stop slave;flush tables"
        #tar zcf /opt/ci123/backup/cishop/$NewFile var
#	/opt/ci123/mysql-5.6.25/bin/mysqldump -S /tmp/mysql3314.sock -p'hanfuboyuan0619' --all-databases --master-data=2|gzip>/opt/ci123/backup/cishop/$NewFile
	/opt/ci123/mysql/bin/mysql -S /tmp/mysql3314.sock -phanfuboyuan0619 -e'show databases'|grep -Ev 'mysql|information_schema|performance_schema|Database'|xargs /opt/ci123/mysql/bin/mysqldump -S /tmp/mysql3314.sock -phanfuboyuan0619 --databases --master-data=2|gzip>/opt/ci123/backup/3314/$NewFile
        /opt/ci123/mysql-5.6.25/bin/mysql -S /tmp/mysql3314.sock -p'hanfuboyuan0619' -e "start slave"
        cd /opt/ci123/backup/3314
#      fi
      echo "[$NewFile]Backup Success!" >> $LogFile
      dateend=$(date +%s)
      let time=$dateend-$datestart
      echo "The Backup Time Is:[$time] " >> $LogFile
      filesize=`ls -l /opt/ci123/backup/3314/$NewFile | awk '{print $5}'`
      if [ $filesize -eq 20 ]
      then
                echo "$NewFile Backup File Size:[$filesize] is error"
                echo "-------------------------------------------"
      fi
      echo "The Backup File Size:[$filesize] " >> $LogFile
#	rsync --bwlimit=1024 -avP -e 'ssh -p 29622' $NewFile 192.168.0.100:/data2/mysql_db_backup/2017/cishop  >> $LogFile
  fi
done
  echo "-------------------------------------------" >> $LogFile
