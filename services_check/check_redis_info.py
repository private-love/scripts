#!/usr/bin python
#coding:utf-8

import paramiko
import re
import time
import string, os, sys  
from datetime import *
import json
import global_functions as func
import Excel
import MySQL

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
        
def check_redis_info(Y,y,m,d):
	"""
	每日检查redis 信息 主体函数
	Y:完整年份 如：2015
	y:年份缩写 如：15
	m：月份
	d：天
	"""
	result = []
	result_mail = []
	err_result = {}
	is_alias_host_eq = False
	total_size = 0
	
	#dbconfig = func.get_db_config()
	#db = MySQL.MySQL(dbconfig)

	#if func.idc_type != 'all':
	#	check_list_sql = "select check_backup.id,check_backup.host_id,check_backup.db,check_backup.path,check_backup.filename,check_backup.send_mail,host.host,host.port,host.alias_host,host.user,host.passwd,host.key_path,check_backup.check_day,host.alias_host from check_backup left join host on check_backup.host_id=host.id where check_backup.is_checking=0 and check_backup.is_delete=0 and host.idc_type='"+str(func.idc_type)+"'"
	#else :
	#	check_list_sql = "select check_backup.id,check_backup.host_id,check_backup.db,check_backup.path,check_backup.filename,check_backup.send_mail,host.host,host.port,host.alias_host,host.user,host.passwd,host.key_path,check_backup.check_day,host.alias_host from check_backup left join host on check_backup.host_id=host.id where check_backup.is_checking=0 and check_backup.is_delete=0"

	#db.query(check_list_sql)
	#check_list = db.fetchAllRows()
   	check_list = ['192.168.0.103:29622','192.168.0.113:29622','192.168.0.244:29622','192.168.0.253:22','192.168.0.240:29622','180.96.68.251:29622','180.96.68.252:29622','180.96.7.115:29622','180.96.7.114:29629','180.96.7.116:29629','118.26.229.9:22','192.168.0.104:29622']

    	for item in check_list:
		hostport = item.split(":")
		host = hostport[0]
		port = int(hostport[1])
		# 检查主机信息
		key = ""
		user = ""
		passwd = ""

		day=datetime.now()
                nowday=day.weekday()
		#if str(nowday) in check_day.split(",") and not is_alias_host_eq :
		if str(nowday) :
        		tc = NewClient()
        		tc.load_system_host_keys()
        		tc._policy = paramiko.AutoAddPolicy()
			isDebug = func.get_config('global_value','isDebug')
			try:
				if not os.path.exists(key):
					key = func.key_path
				if not user :
					user = func.key_user

                		tc.connect(host,port=port, username=user, password=passwd,key_filename=key, timeout=10) 
				
				stdin, stdout, stderr, status = tc.call("ps aux|grep redis-server|grep -v 'grep' |awk '{print $2\"###\"$11\"###\"$12}'")
				data = stdout.read()
				res = data.split("\n")
				for line in res :
					if line :
						redis_info_dict = {}
						tmp_list = line.split("###")
						if len(tmp_list) == 3 :
							pid_thread = tmp_list[0]
							path_thread = tmp_list[1]
							other_thread = tmp_list[2]
							if pid_thread > 0 :
								net_str = "netstat -nltp |grep '"+str(pid_thread)+"/redis-server'|head -n 1|awk '{print $4}'"
								lsof_str = "lsof -p "+str(pid_thread)+" |grep 'redis-server'|awk '{print $NF}'"
								stdin1, stdout1, stderr1, status1 = tc.call(net_str)
								stdin2, stdout2, stderr2, status2 = tc.call(lsof_str)
								host_port = stdout1.read().strip()
								path_real = stdout2.read().strip()
								path_bin = os.path.dirname(path_real)
								path_bin_cli = path_bin+"/redis-cli"
							else :
								return ['pid not exisit']
						host_post_list = host_port.strip().split(':')
						redis_host = host_post_list[0]
						redis_port = host_post_list[1]
						stdin3, stdout3, stderr3, status3 = tc.call(path_bin_cli+" -h "+str(redis_host)+" -p "+str(redis_port)+" -a foo info")
						redis_info_data_str = stdout3.read()
						if not status3 :
							redis_info_list = redis_info_data_str.split("\n")
						else :
							return ['redis info data null']
					
						for line in redis_info_list :
                        				if line.strip() and not line.strip().startswith("#") :
                                				line_tmp = line.strip().split(":")
                                				redis_info_dict[line_tmp[0]] = line_tmp[1]
						
						stdin4, stdout4, stderr4, status4 = tc.call(path_bin_cli+" -h "+str(redis_host)+" -p "+str(redis_port)+" -a foo config get maxmemory|awk '{print $1}'|tail -n 1")
						redis_maxmemory_str = stdout4.read()
                                                if not status4 :
							redis_info_dict['maxmemory'] = redis_maxmemory_str.strip()
                                                else :
                                                        return ['redis maxmemory null']

						if int(redis_info_dict['used_memory']) <= int(redis_info_dict['maxmemory']) and int(redis_info_dict['used_memory']) > 0  :
							redis_info_dict['used_ratio'] = round(float(redis_info_dict['used_memory'])/float(redis_info_dict['maxmemory']),2) * 100
						else :
							redis_info_dict['used_ratio'] = 0	

						list = [host+','+redis_host+':'+redis_port+','+redis_info_dict['redis_version']+','+redis_info_dict['connected_clients']+','+str(redis_info_dict['used_ratio'])+'%,'+redis_info_dict['used_memory']+','+redis_info_dict['used_memory_human']+','+redis_info_dict['used_memory_rss']+','+redis_info_dict['used_memory_peak']+','+redis_info_dict['used_memory_peak_human']+','+datetime.utcfromtimestamp(float(redis_info_dict['rdb_last_save_time'])).strftime("%Y-%m-%d %H:%H:%S")+','+redis_info_dict['rdb_changes_since_last_save']+','+redis_info_dict['arch_bits']+','+redis_info_dict['gcc_version']+','+redis_info_dict['process_id']+','+redis_info_dict['uptime_in_seconds']+','+redis_info_dict['uptime_in_days']]
						list_mail = [host+','+redis_host+':'+redis_port+','+redis_info_dict['redis_version']+','+redis_info_dict['connected_clients']+','+str(redis_info_dict['used_ratio'])+'%,'+redis_info_dict['used_memory_human']+','+func.convertBytes(float(redis_info_dict['maxmemory']))+','+datetime.utcfromtimestamp(float(redis_info_dict['rdb_last_save_time'])).strftime("%Y-%m-%d %H:%H:%S")+','+redis_info_dict['rdb_changes_since_last_save']+','+redis_info_dict['process_id']+','+redis_info_dict['uptime_in_days']]

						if isDebug :
                                                        print list_mail

						result.append(list)
						result_mail.append(list_mail)
                	        stdout.close()
                	        stdin.close()
                	except Exception as err:
				print "error"+str(id)+"###"+str(err)
				err_result[host] = str(id)+"###"+str(err)
				continue

        	tc.close()
	if total_size :
		total_size_str = func.convertBytes(total_size)
	else :
		total_size_str = "0b"
	return result,result_mail,err_result,total_size_str

if __name__ == '__main__':
        is_auto = False

        if len(sys.argv) == 5:
                is_auto = False
                Y = sys.argv[1]
                y = sys.argv[2]
                m = sys.argv[3]
                d = sys.argv[4]
        else:
                is_auto =True
                Y = (datetime.now()).strftime('%Y')
                y = (datetime.now()).strftime('%y')
                m = (datetime.now()).strftime('%m')
                d = (datetime.now()).strftime('%d')

	h = (datetime.now()).strftime('%H')
	M = (datetime.now()).strftime('%M')
	S = (datetime.now()).strftime('%S')

	isSendMail=func.get_config('global_value','isSendMail')
	#主题调用函数
	result,result_mail,err_result,total_size_str = check_redis_info(Y,y,m,d)

	if len(result) > 1 :
		att_filename = "xls/redis_list_"+str(Y)+"-"+str(m)+"-"+str(d)+"_"+str(h)+str(M)+str(S)+".xlsx"
		hdngs = ['服务器IP', '服务端口','redis版本','连接数','容量使用率','内存大小','内存容量','内存总量','内存峰值','峰值容量','最新保存时间','执行命令数','位数','gcc版本','进程ID','在线时间','在线天数']
		exc_ins = Excel.Excel(att_filename,sheet_name='ciSheet', encoding='utf-8')
		exc_ins.backup_xlsx_write(hdngs, result)

	if is_auto and isSendMail == 'yes' and len(result_mail) > 1 :
		hdngs_mail = ['服务器IP', '服务端口','redis版本','连接数','容量使用率','内存容量','内存总量','最新保存时间','执行命令数','进程ID','在线天数']
		content=func.toHtml(hdngs_mail,result_mail,total_size_str)
		sub="redis服务每日统计("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		#func.send_mail(func.mailto_list,sub,content)
		func.sendMail(sub,content,func.mailto_list,att_filename)
	else:
		print json.dumps('suc!')

	if len(err_result) > 0 and isSendMail == 'yes' :
		err_sub = "redis服务检查存在错误("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		err_content = func.toErrHtml(err_result)
		func.send_mail(func.mailto_list, err_sub, err_content)
	
