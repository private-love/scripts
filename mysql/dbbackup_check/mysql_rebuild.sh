#!/bin/sh
#set password for root@localhost = password('xxx')
#delete from user where Password='';
i=3675
while true
do
  netstat -nltp|grep $i  > /dev/null 2>&1
  [ $? != 0 ] && break || i=`expr $i + 1`
done
port=$i
dir="wlx_$port"
server=$port$port
mysqlversion=`ls /opt/ci123|grep 'mysql'|grep -v proxy|tail -1`
function_my_cnf()
{
echo "[client]
character-set-server = utf8
port    = $port
socket  = /tmp/mysql$port.sock

[mysqld]
character-set-server = utf8
user    = mysql
port    = $port
socket  = /tmp/mysql$port.sock
datadir = /opt/ci123/data/$dir/var
log-error = /opt/ci123/data/$dir/log/mysql_error.log
pid-file = /opt/ci123/data/$dir/log/mysql.pid
open_files_limit    = 10240
back_log = 600
max_connections = 500
max_connect_errors = 600
external-locking = FALSE
max_allowed_packet = 1024M
sort_buffer_size = 8M
join_buffer_size = 1M
thread_cache_size = 300
query_cache_size = 512M
query_cache_limit = 32M
query_cache_min_res_unit = 2k
thread_stack = 192K
transaction_isolation = READ-COMMITTED
tmp_table_size = 246M
max_heap_table_size = 246M
long_query_time = 3
log-slave-updates
log-bin = /opt/ci123/data/$dir/log/bin-log
binlog_cache_size = 64M
binlog_format = MIXED
max_binlog_cache_size = 128M
max_binlog_size = 1G
relay-log-index = /opt/ci123/data/$dir/log/relay-bin.index
relay-log-info-file = /opt/ci123/data/$dir/log/relay-bin.info
relay-log = /opt/ci123/data/$dir/log/relay-bin
expire_logs_days = 0
key_buffer_size = 256M
read_buffer_size = 1M
read_rnd_buffer_size = 16M
bulk_insert_buffer_size = 64M
myisam_sort_buffer_size = 128M
myisam_max_sort_file_size = 10G
myisam_repair_threads = 1
myisam_recover
interactive_timeout = 1200
wait_timeout = 1200
skip-name-resolve
server-id = $server

slow-query-log=ON
long_query_time = 3

[mysqldump]
quick
max_allowed_packet = 64M
">/opt/ci123/data/$dir/my.cnf
}

function_dir()
{
if [ ! -d "/opt/ci123/data/$dir/var/" ];
then
    mkdir -p /opt/ci123/data/$dir/var/
else
    echo "/opt/ci123/data/$dir/var/" 已存在
fi
if [ ! -d "/opt/ci123/data/$dir/log/slow" ];
then
    mkdir -p /opt/ci123/data/$dir/log/slow
else
    echo "/opt/ci123/data/$dir/log/slow" 已存在
fi
}

function_chowndir()
{
  chown mysql:mysql -R /opt/ci123/data/$dir/
}

function_dbuser()
{
if  [[ "$mysqlversion" =~ "5.6" ]]
then
cd /opt/ci123/$mysqlversion/
./scripts/mysql_install_db --defaults-file=/opt/ci123/data/$dir/my.cnf --datadir=/opt/ci123/data/$dir/var/ --user=mysql  > /dev/null 2>&1
else
cd /opt/ci123/$mysqlversion/
./bin/mysql_install_db --defaults-file=/opt/ci123/data/$dir/my.cnf --datadir=/opt/ci123/data/$dir/var/ --user=mysql  > /dev/null 2>&1
fi
}
function deletedb() {
/opt/ci123/$mysqlversion/bin/mysqladmin -S /tmp/mysql$port.sock shutdown  > /dev/null 2>&1
sleep 2
/bin/rm -rf /opt/ci123/data/$dir
}
function_dir
function_my_cnf
function_chowndir
function_dbuser
/opt/ci123/$mysqlversion/bin/mysqld_safe --defaults-file=/opt/ci123/data/$dir/my.cnf --datadir=/opt/ci123/data/$dir/var/ --user=mysql &  > /dev/null 2>&1
sleep 3
ps aux|grep $mysqlversion|grep -v grep|grep $port  > /dev/null 2>&1
if [[ $? == 1 ]]
then 
  echo 'mysql start error'
else
  gzip -d $1
  filename=${1%???}
  filetype=`file $filename` 
  if [[ $filetype =~ "tar" ]]
  then
    cd /opt/ci123/data/$dir/
    tar xvf $filename > /dev/null 2>&1
  else
    /opt/ci123/$mysqlversion/bin/mysql -S /tmp/mysql$port.sock -e 'source $filename;'
  fi
  gzip $filename
fi
ps aux|grep $mysqlversion|grep -v grep|grep $port  > /dev/null 2>&1
if [[ $? == 1 ]]
then
  echo 'error';echo 'error';echo 'error'
else
dbnames=`/opt/ci123/$mysqlversion/bin/mysql -S /tmp/mysql$port.sock -e 'show databases'|grep -Ev 'Database|information_schema|test|mysql'`
lendbs=`/opt/ci123/$mysqlversion/bin/mysql -S /tmp/mysql$port.sock -e 'show databases'|grep -Ev 'Database|information_schema|test|mysql'|wc -l`
tablesnum=""
datanum=""
if [[ $lendbs != 0 ]]
then
    for x in $dbnames
    do
       count=0
       tables=`/opt/ci123/$mysqlversion/bin/mysql -S /tmp/mysql$port.sock -e "use $x;show tables"|grep -v Tables_in_`
       lentables=`/opt/ci123/$mysqlversion/bin/mysql -S /tmp/mysql$port.sock -e "use $x;show tables"|grep -v  Tables_in_|wc -l`
       if [[ $tablesnum == "" ]]
       then 
           tablesnum=$lentables
       else
           tablesnum=$tablesnum,$lentables
       fi
       for y in $tables
       do
           counttable=`/opt/ci123/$mysqlversion/bin/mysql -S /tmp/mysql$port.sock -e "use $x;select count(*) from $y"|grep -v count`
           if [[ $count == 0 ]]
           then 
               count=$counttable
           else
               count=`expr $count + $counttable`
           fi
       done
       if [[ $datanum == "" ]]
       then 
           datanum=$count
       else
           datanum=$datanum,$count
       fi
        echo $count
    done
    deletedb
    echo $lendbs 
    echo $tablesnum
    echo $datanum
else
deletedb
echo 0
echo 0
echo 0
fi
fi
