#!/usr/bin python
#coding:utf-8
#what check backup version 2.1
#when 2016-05-10 
#author: v1.0 feijilei v2.0 wuwanli v2.1 chen-123

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
        
def check_mount_info(Y,y,m,d):
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
	
	check_list = ['192.168.0.103:29622','192.168.0.108:29622','192.168.0.113:29622','192.168.0.244:29622','192.168.0.253:22','192.168.0.240:29622','180.96.68.251:29622','180.96.68.252:29622','180.96.7.115:29622','180.96.7.114:29622','180.96.7.114:29629','180.96.7.116:29629','180.96.7.116:29622','192.168.0.104:29622']

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
				
				stdin, stdout, stderr, status = tc.call("ls -lf /opt/ci123/apache/logs/|sed '1d'|sed '/access/!d'|awk '{print $NF}'|grep -E '"+str(m)+str(d)+"|"+str(m)+"-"+str(d)+"'|awk -F'-access' '{print $1}'")
				data = stdout.read()
				res = data.split("\n")
				for line in res :
					if line :
						tmp_list = line.split()
						if len(tmp_list) == 1 :
							apache_log_name = tmp_list[0]

						list = [host+','+apache_log_name]

						if isDebug :
                                                        print list

						result.append(list)
						result_mail.append(list)
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
	result,result_mail,err_result,total_size_str = check_mount_info(Y,y,m,d)

	if len(result) > 1 :
		att_filename = "xls/apache_loglist_"+str(Y)+"-"+str(m)+"-"+str(d)+"_"+str(h)+str(M)+str(S)+".xlsx"
		hdngs = ['服务器IP', '在线域名']
		exc_ins = Excel.Excel(att_filename,sheet_name='ciSheet', encoding='utf-8')
		exc_ins.backup_xlsx_write(hdngs, result)

	if is_auto and isSendMail == 'yes' and len(result_mail) > 1 :
		hdngs_mail = ['服务器IP', '在线域名']
		content=func.toHtml(hdngs_mail,result_mail,total_size_str)
		sub="服务器apache在线域名--每日统计("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		#func.send_mail(func.mailto_list,sub,content)
		func.sendMail(sub,content,func.mailto_list,att_filename)
	else:
		print json.dumps('suc!')

	if len(err_result) > 0 and isSendMail == 'yes' :
		err_sub = "服务器apache在线域名检查存在错误("+str(Y)+'-'+str(m)+'-'+str(d)+")"
		err_content = func.toErrHtml(err_result)
		func.send_mail(func.mailto_list, err_sub, err_content)
	
