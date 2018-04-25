#!/bin/sh
set -e

mysql_port="3338"
datadir="nbg_test2_3338"
mysql_username="root"
mysql_password="xxx"

function_start_mysql()
{
    printf "Starting MySQL...\n"
    /opt/ci123/mysql-5.6.20/bin/mysqld_safe --defaults-file=/opt/ci123/data/${datadir}/my.cnf &
}

function_connect_mysql()
{
    printf "Connecting to  ${datadir}...\n"
    /opt/ci123/mysql-5.6.20/bin/mysql -u root -S /tmp/mysql${mysql_port}.sock -p${mysql_password}
}

function_stop_mysql()
{
    printf "Stoping MySQL...\n"
    /opt/ci123/mysql-5.6.20/bin/mysqladmin -u ${mysql_username} -p${mysql_password} -S /tmp/mysql${mysql_port}.sock shutdown
}

function_restart_mysql()
{
    printf "Restarting MySQL...\n"
    function_stop_mysql
    sleep 5
    function_start_mysql
}

function_kill_mysql()
{
    kill -9 $(ps -ef | grep 'bin/mysqld_safe' | grep ${mysql_port} | awk '{printf $2}')
    kill -9 $(ps -ef | grep 'bin/mysqld' | grep ${mysql_port} | awk '{printf $2}')
}

if [ "$1" = "start" ]; then
    function_start_mysql
elif [ "$1" = "conn" ]; then
    function_connect_mysql
elif [ "$1" = "stop" ]; then
    function_stop_mysql
elif [ "$1" = "restart" ]; then
    function_restart_mysql
elif [ "$1" = "kill" ]; then
    function_kill_mysql
else
    printf "Usage: ./mysql.sh {start|conn|stop|restart|kill}\n"
fi
