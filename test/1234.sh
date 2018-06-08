while true
do
    echo $1 start
    flock -xn ./.test.lock -c 'sh 123.sh "$1"'
    [ $? -ne 0 ] && sleep 30 || break
done
