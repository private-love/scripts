#!/usr/bin python
# coding:utf-8
import paramiko
import sys
import global_functions as func
import MySQL
from sendhtml import sendmail
import socket
import multiprocessing
reload(sys)
sys.setdefaultencoding('utf-8')
def check_db(item):
    if func.idc_type == 'all':
        host = str(item[13])
    else:
        host = str(item[6])
    port = int(item[7])
    backup_dir = item[3]
    file_name = item[5]
    complete_file = backup_dir + '/' + file_name
    private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
    tc = paramiko.SSHClient()
    tc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        tc.connect(hostname=host, port=port, username="root", pkey=private_key, timeout=10)
        hostinfo = item[6].split(':')
        if len(hostinfo) == 2:
            ip = hostinfo[0]
            port = hostinfo[1]
            command = 'ssh ' + str(ip) + ' -p ' + str(port) + " 'cd /opt/scripts/wlx/;sh mysql_rebuild.sh " + complete_file + "'"
            stdin, stdout, stderr = tc.exec_command(command)
        else:
            command = "cd /opt/scripts/wlx/;sh mysql_rebuild.sh " + complete_file
            stdin, stdout, stderr = tc.exec_command(command)
        print(command)
        data = stdout.read()
        datalist = data.strip().split("\n")
        print(datalist)
        datalist = datalist[-3:]
        datalist.append(backup_dir)
        datalist.append(file_name)
        print(datalist)
        return datalist
    except Exception as err:
        print("error" + str(host) + "###" + str(err))
    tc.close()

def check_backup():
    dbconfig = func.get_db_config()
    db = MySQL.MySQL(dbconfig)

    if func.idc_type != 'all':
        check_list_sql = "select check_backup.id,check_backup.host_id,check_backup.db,check_backup.path,check_backup.filename,check_backup.last_check_filename,host.host,host.port,host.alias_host,host.user,host.passwd,host.key_path,check_backup.check_day,host.alias_host from check_backup left join host on check_backup.host_id=host.id where check_backup.is_checking=0 and check_backup.is_delete=0 and check_backup.last_check_filename != '' and host.idc_type='" + str(func.idc_type) + "'"
    else:
        check_list_sql = "select check_backup.id,check_backup.host_id,check_backup.db,check_backup.path,check_backup.filename,check_backup.last_check_filename,host.host,host.port,host.alias_host,host.user,host.passwd,host.key_path,check_backup.check_day,host.alias_host from check_backup left join host on check_backup.host_id=host.id where check_backup.is_checking=0 and check_backup.is_delete=0 and check_backup.last_check_filename != '' and check_backup.db='helptable' or check_backup.db='news' or check_backup.db='shop_shequ_db' or check_backup.db='tc_db' or check_backup.db='group' or check_backup.db='mobile_shiyong' or check_backup.db='ciphoto' or check_backup.db='happy_city' or check_backup.db='kaixintreedb'"

    db.query(check_list_sql)
    check_list = db.fetchAllRows()
    dictall = {}
#    pronum = len(check_list)
#    print(pronum)
#    p = multiprocessing.Pool(processes=pronum)
#    datalists = p.map(check_db,check_list)
#    print(datalists)
#    p.close()
#    p.join()
#    for i in range(len(check_list)):
#        item = check_list[i]
#        dictdb = {}
#        if func.idc_type == 'all':
#            host = str(item[13])
#        else:
#            host = str(item[6])
#        backup_name = item[2]
#        datalist = datalists[i]
#        print(datalist)
#        hostinfo = item[6].split(':')
#        if len(hostinfo) == 2:
#            host = str(hostinfo[0])
#        if dictall.has_key(str(host)):
#            dictall[str(host)][backup_name] = datalist
#        else:
#            dictdb[backup_name] = datalist
#            dictall[str(host)] = dictdb
    for item in check_list:
        dictdb = {}
        if func.idc_type == 'all':
            host = str(item[13])
        else:
            host = str(item[6])
        backup_name = item[2]
        datalist = check_db(item)
        print(datalist)
        hostinfo = item[6].split(':')
        if len(hostinfo) == 2:
            host = str(hostinfo[0])
        if dictall.has_key(str(host)):
            dictall[str(host)][backup_name] = datalist
        else:
            dictdb[backup_name] = datalist
            dictall[str(host)] = dictdb
    print(dictall)
    return dictall
def tohtml(dict):
    html = "<head><style>td {text-align:center}</style><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head>" \
           "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\"><th>IP</th><th>数据库实例</th><th>备份文件目录</th><th>依赖备份文件名</th><th>实例中库数量</th><th>库中表数量</th><th>库中数据总量</th><th>实例数据总和</th></tr><tr style=\"text-align:center;\">"
    keys_list = dict.keys()
    keys_list = sorted(keys_list, key=socket.inet_aton)
    for key in keys_list:
        dblen = len(dict[key])
        html += "<td rowspan=" + str(dblen) + ">" + key + "</td>"
        for db in dict[key]:
            if dict[key][db]:
                if dict[key][db][0] != "error":
                    alldata = dict[key][db][2].split(",")
                    alldata = list(map(int, alldata))
                    alldatasum = str(sum(alldata))
                else:
                    alldatasum = "error"
                if dict[key][db][0] != "error":
                    html += "<td>" + str(db) + "</td><td>" + str(dict[key][db][3]) + "</td><td>" + str(dict[key][db][4]) + "</td><td>" + str(dict[key][db][0]) + \
                            "</td><td>" + str(dict[key][db][1]) + "</td><td>" + str(dict[key][db][2]) + "</td><td>" + alldatasum + "</td></tr><tr style=\"text-align:center;\">"
                else:
                     html += "<td style=background:red>" + str(db) + "</td><td style=background:red>" + str(dict[key][db][3]) + "</td><td style=background:red>" + str(dict[key][db][4]) + "</td><td style=background:red>" + str(dict[key][db][0]) + "</td><td style=background:red>" + str(dict[key][db][1]) + "</td><td style=background:red>" + str(dict[key][db][2]) + "</td><td style=background:red>" + alldatasum + "</td></tr><tr style=\"text-align:center;\">"
            else:
                html += "<td>" + str(db) + "</td>" + "<td colspan=5>None</td></tr><tr style=\"text-align:center;\">"
    html += "</tr></table>"
    print(html)
    return html
if __name__ == '__main__':
    dictallget = check_backup()
    print("look then")
    print(dictallget)
    #dictallget = {'221.231.140.243': {u'news': ['error', 'error', 'error', u'/opt/ci123/backup/news', u'dbnews180516.tar.gz'], u'shop_shequ_db': ['0', '0', '0', u'/opt/ci123/backup/guang', u'dbshop_shequ180516.tar.gz']}, '192.168.1.103': {u'helptable': ['1', '151', '6702417', u'/data1/mysqldatabak/helptable', u'dbhelptable180514.tar.gz']}}
    html = tohtml(dictallget)
    sendmail(html)
