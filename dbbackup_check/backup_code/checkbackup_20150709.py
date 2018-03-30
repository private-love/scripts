#!/usr/bin python
#coding:utf-8

import paramiko
import re
import time
import string, os, sys  
from datetime import *
import json
import global_functions as func

reload(sys)
sys.setdefaultencoding('utf-8')

class NewClient(paramiko.SSHClient):
    def call(self, command, bufsize=-1):
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        status = chan.recv_exit_status()
        return stdin, stdout, stderr, status
        
def check_backup(Y,y,m,d):
	"""
	每日检查数据库备份计划 主体函数
	Y:完整年份 如：2015
	y:年份缩写 如：15
	m：月份
	d：天
	"""
	result = []
	err_result = {}
	is_alias_host_eq = False
	total_size = 0

	if func.idc_type != 'all':
		check_list_sql = "select check_backup.id,check_backup.host_id,check_backup.db,check_backup.path,check_backup.filename,check_backup.send_mail,host.host,host.port,host.alias_host,host.user,host.passwd,host.key_path,check_backup.check_day,host.alias_host from check_backup left join host on check_backup.host_id=host.id where check_backup.is_checking=0 and check_backup.is_delete=0 and host.idc_type='"+str(func.idc_type)+"'"
	else :
		check_list_sql = "select check_backup.id,check_backup.host_id,check_backup.db,check_backup.path,check_backup.filename,check_backup.send_mail,host.host,host.port,host.alias_host,host.user,host.passwd,host.key_path,check_backup.check_day,host.alias_host from check_backup left join host on check_backup.host_id=host.id where check_backup.is_checking=0 and check_backup.is_delete=0"

	check_list = func.mysql_query(check_list_sql)

    	for item in check_list:
		# 检查主机信息
		id = item[1]
		if func.idc_type == 'all' :
			host = str(item[13])
		else :
			host = str(item[6])
		
		if str(item[13]) == str(item[6]) and func.idc_type == 'all' and item[6].startswith('192.168'):
			is_alias_host_eq = True
		
		port = int(item[7])
		user = item[9]
		passwd = str(item[10])
		key = str(item[11])
		# 数据库检查项信息
		back_id = item[0]
		backup_name = item[2]
                backup_dir = item[3]
                file_name = item[4]
                file_name = file_name.replace('%y',y).replace('%Y',Y).replace('%m',m).replace('%d',d)
                backup_dir = backup_dir.replace('%y',y).replace('%Y',Y).replace('%m',m).replace('%d',d)
		check_day = item[12]

		day=datetime.now()
                nowday=day.weekday()
		if str(nowday) in check_day.split(",") and not is_alias_host_eq :
        		tc = NewClient()
        		tc.load_system_host_keys()
        		tc._policy = paramiko.AutoAddPolicy()
			isDebug = func.get_config('global_value','isDebug')
			try:
				#print host,port,user,passwd,key,":"+check_day
				if not os.path.exists(key):
					key = func.key_path
					#key = '/opt/scripts/dbbackup_check/ci123dev'
				if not user :
					user = func.key_user

                		tc.connect(host,port=port, username=user, password=passwd,key_filename=key, timeout=10) 
				stdin, stdout, stderr, status = tc.call('cd '+str(backup_dir)+';ls -gGHrtl --full-time '+str(file_name))
				data=stdout.read()
                	        data=re.sub(" +", " ", data)
                	        res=data.split(' ')
				try:
                	        	b_time = res[3]+' '+res[4].split('.')[0]
                	                b_size = res[2]
                	                b_name = res[-1].strip()
					total_size += string.atof(b_size)
					b_size_str = func.convertBytes(string.atof(b_size))
					
                	                if isDebug == 'yes':
						print b_time,b_size,b_name,b_size_str
                	                        print host,'\033[1;31;40m',backup_name,'\033[0m',b_time,'\033[1;36;40m',b_size_str,'\033[0m',b_name,'\033[1;34;40m',backup_dir,'\033[0m'
                	        except:
                	                b_time = ''
                	                b_size = ''
					b_size_str = ''
                	                b_name = ''
                	                if isDebug == 'yes':
                	                        print host,'\033[1;31;40m',backup_name,'\033[0m','\033[1;37;41m','warning!!','\033[0m'
                	        if not b_size:
					#insert_backup_checklog_sql = "insert into check_backup_log (`bid`,`db_name`,`size`,`date`) values ('"+str(id)+"','"+str(b_name)+"','"+str(b_size)+"','"+str(Y)+"')"
                	                update_sql = "update `check_backup` set `size`=' ' where id="+str(back_id)+" limit 1"
                	        else:
                	                update_sql = "update `check_backup` set `size`='"+b_size+"',`last_check_filename`='"+str(b_name)+"',`last_check_time`='"+str(b_time)+"' where id="+str(back_id)+" limit 1"
				
				file_backup_date = str(Y)+"-"+str(m)+"-"+str(d)
				insert_backup_checklog_sql = "insert into check_backup_log (`bid`,`host_id`,`db_name`,`size`,`date`) values ('"+str(back_id)+"','"+str(id)+"','"+str(b_name)+"','"+str(b_size)+"','"+str(file_backup_date)+"')"
				if not b_name or not b_size :
					insert_backuplog_alarm = "insert into alarm_checkbackup_history (`idc_type`,`b_id`,`server_id`,`check_type`,`alarm_type`,`alarm_value`,`level`,`message`,`send_mail`,`send_mail_status`) value ('"+func.idc_type+"','"+str(back_id)+"','"+str(id)+"','"+str("checkbakup")+"','"+str("check_db")+"','"+str("数据库备份出错，请检查！")+"','"+str("warning")+"','"+str("检查路径和服务器ip是否配置正确。")+"','1','0')"
					func.mysql_exec(insert_backuplog_alarm,[])
				#print insert_backup_checklog_sql
				func.mysql_exec(update_sql,[])
				func.mysql_exec(insert_backup_checklog_sql,[])
                	        list=[host+','+backup_name+','+b_time+','+b_size_str+','+b_name+','+backup_dir]
                	        result.append(list)
                	        stdout.close()
                	        stdin.close()
                	except Exception as err:
				err_result[host] = str(id)+"###"+str(err)
				continue

        	tc.close()
	total_size_str = func.convertBytes(total_size)
	return result,err_result,total_size_str

if __name__ == '__main__':
        is_auto = False

        if len(sys.argv) == 5:
                is_auto = False
                Y=sys.argv[1]
                y=sys.argv[2]
                m=sys.argv[3]
                d=sys.argv[4]
        else:
                is_auto =True
                Y=(datetime.now() - timedelta(days=1)).strftime('%Y')
                y=(datetime.now() - timedelta(days=1)).strftime('%y')
                m=(datetime.now() - timedelta(days=1)).strftime('%m')
                d=(datetime.now() - timedelta(days=1)).strftime('%d')

	isSendMail=func.get_config('global_value','isSendMail')
	#主题调用函数
	result,err_result,total_size_str = check_backup(Y,y,m,d)

	if is_auto:
		content=func.toHtml(result,total_size_str)
		sub="服务器备份每日统计("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		if isSendMail == 'yes' :
			func.send_mail(func.mailto_list,sub,content)
	else:
		print json.dumps('suc!')

	if len(err_result) > 0:
		err_sub = "备件检查存在错误("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		err_content = func.toErrHtml(err_result)
		if isSendMail == 'yes' :
			func.send_mail(func.mailto_list, err_sub, err_content)
	
