#!/bin/sh
#set password for root@localhost = password('xxx')
#delete from user where Password='';
port="3338"
dir="nbg_test2_3338"
server="663338"
mysqlversion="mysql-5.6.20"
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
#basedir = /opt/ci123/mysql-5.6.20
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
#thread_concurrency = 8
query_cache_size = 512M
query_cache_limit = 32M
query_cache_min_res_unit = 2k
#default-storage-engine = InnoDB
thread_stack = 192K
transaction_isolation = READ-COMMITTED
tmp_table_size = 246M
max_heap_table_size = 246M
long_query_time = 3
log-slave-updates
log-bin = /opt/ci123/data/$dir/log/nbg-bin
binlog_cache_size = 64M
binlog_format = MIXED
max_binlog_cache_size = 128M
max_binlog_size = 1G
relay-log-index = /opt/ci123/data/$dir/log/nbg-relay-bin.index
relay-log-info-file = /opt/ci123/data/$dir/log/nbg-relay-bin.info
relay-log = /opt/ci123/data/$dir/log/nbg-relay-bin
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
#master-connect-retry = 10
#slave-skip-errors = 1032,1062,126,1114,1146,1048,1396
#replicate-ignore-db=mysql


server-id = $server

innodb_additional_mem_pool_size = 16M
innodb_buffer_pool_size = 4G
innodb_data_file_path = ibdata1:256M:autoextend
innodb_file_io_threads = 4
innodb_thread_concurrency = 8
innodb_flush_log_at_trx_commit = 2
innodb_log_buffer_size = 16M
innodb_log_file_size = 128M
innodb_log_files_in_group = 3
innodb_max_dirty_pages_pct = 90
innodb_lock_wait_timeout = 120
innodb_file_per_table = 1

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
cd /opt/ci123/$mysqlversion/
./scripts/mysql_install_db --defaults-file=/opt/ci123/data/$dir/my.cnf --datadir=/opt/ci123/data/$dir/var/	
}

function_dir
function_my_cnf
function_chowndir
function_dbuser
