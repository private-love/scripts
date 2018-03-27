#!/usr/bin python
#coding:utf-8
#what check backup
#who  by feijilei
#when 2013-09-05
#modify by wuwangli @2014-06-11

import paramiko
import re
import time
import ConfigParser  
import string, os, sys  
from datetime import *
from email.mime.text import MIMEText
import socket 
import smtplib
import MySQLdb
import json

reload(sys)
sys.setdefaultencoding('utf-8')
#mailto_list=["chenwenping@corp-ci.com"]
#mailto_list=["cjy@corp-ci.com","wuwanli@corp-ci.com"]
mailto_list=["jiarong@corp-ci.com"]
mail_host="smtp.163.com"
mail_user="ci123webserver@163.com"
mail_pass="ci123webserver12"
mail_postfix="163.com"
def send_mail(to_list,sub,content):
    me=mail_user
    msg = MIMEText(content,'html', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me,to_list,msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

def connect_db():
	conn = MySQLdb.connect(host='127.0.0.1',user='ci123',passwd='cifuyuan1906_!@#',port=3312,db='ci123',charset='utf8')
	cursor = conn.cursor()
	return cursor
	
result=[]
err_result = {} 
class NewClient(paramiko.SSHClient):
    def call(self, command, bufsize=-1):
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        status = chan.recv_exit_status()
        return stdin, stdout, stderr, status
        
def toErrHtml(dict):
	html = ""
    	html += "<table width=\"600\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    	html += "<tr style=\"text-align:center;\"><td>服务器</td><td>原因</td></tr>"
	for key,value in dict.items():
		list = value.split('###')
		id = list[0]
		reason = list[1]
            	html += "<tr align=\"justify\" >"
            	html += "<td nowrap=\"nowrap\" style=\"padding:0px 10px;\">"
            	html += "<a href=\"http://racktables.ci123.com:88/backup/backup_host_add.php?id="+id+"\" target=\"_blank\">"+str(key)+"</a>"
            	html += "</td>"
		
            	html += "<td nowrap=\"nowrap\" style=\"padding:0px 10px;\">"
            	html += str(reason)
            	html += "</td>"
            	html += "</tr>"
	html += "</table>"
	return html
def toHtml(list):
    #把list转换为dict
    dict = {}
    key_list = []
    for line in list:
        line = line[0]
        line = line.split(',')
        key = line[0]
        value = line[1:]
        if key not in dict:
            key_list.append(key)
            dict[key] = []
            dict[key].append(value)
        else:
            dict[key].append(value)

    #写成html表格
    html = ""
    html += "<table width=\"600\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\"><td>IP</td><td>备份</td><td>备份日期</td><td style=\"text-align:center;\">大小</td><td>文件</td><td>文件夹路径</td></tr>"
    count = True
    for key in key_list:
        data = dict[key]
        n = len(data)
        for d in data:
            html += "<tr align=\"justify\" >"
            if(count):
                html += "<td nowrap=\"nowrap\" rowspan="+ str(n) +" style=\"padding:0px 10px;\">"
                html += str(key)
                html += "</td>"
                count = False
            iserror = not d[-2].strip(" ")
            for i in d:
                if (not i.strip(' ')):
                    html += "<td nowrap=\"nowrap\" bgcolor=\"red\" style=\"padding:0px 10px;\">"
                    html += str('backup error')
                else:
                    if iserror:
                        html += "<td nowrap=\"nowrap\" bgcolor=\"red\" style=\"padding:0px 10px;\">"
                        html += str(i)
                    else:
                        html += "<td nowrap=\"nowrap\" style=\"padding:0px 10px;\">"
                        html += str(i)
                html += "</td>"
            html += "</tr>"
        count = True
    html += "</table>"

    return html
def insertLog(year, month, day, cursor):
	sql = "insert into `check_log` (day, dated) values('"+year+"-"+month+"-"+day+"', '"+(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')+"')"
	cursor.execute(sql)
	return True	

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
	cursor = connect_db()
	insertLog(Y, m, d, cursor)
	cursor.execute('select * from host limit 100')
	allhost = cursor.fetchall()
	for item in allhost:
		id = item[0]
		host = str(item[1])
		port = int(item[2])
		user = item[3]
		passwd = str(item[4])
		key = str(item[5])
		#print host
        	tc = NewClient()
        	tc.load_system_host_keys()
        	tc._policy = paramiko.AutoAddPolicy()
		try:
			key = '/opt/scripts/dbbackup_check/'+key
                	tc.connect(host,port=port, username=user, password=passwd,key_filename=key, timeout=10) #timeout为5秒
                except Exception as err:#链接超时或者错误 返回err continue
			#print err
			err_result[host] = str(id)+"###"+str(err)
			continue

		d=datetime.now()
                nowday=d.weekday()
		print nowday
		if d in [1,3,5]:
			cursor.execute('select * from check_backup where host_id='+str(id)+' limit 20')
			allback = cursor.fetchall()

		else:
			cursor.execute('select * from check_backup where host_id='+str(id)+' and id !=3 and id !=4 limit 20')
                        allback = cursor.fetchall()

		for bitem in allback:
			print bitem
#			back_id = bitem[0]
#		        backup_name=bitem[2]
#		        backup_dir=bitem[3]
#		        file_name=bitem[4]
#        	  	file_name=file_name.replace('%y',y).replace('%Y',Y).replace('%m',m).replace('%d',d)
#        	    	backup_dir=backup_dir.replace('%y',y).replace('%Y',Y).replace('%m',m).replace('%d',d)
#       	    	#stdin, stdout, stderr, status = tc.call(
#        	    	#    cd /opt/ci123/backup;ls -gGhQHrtl --full-time|awk 'NR>1{print $0}'|awk '{for(i=1;i<NF;i++)printf $i"   "}{system("du -sh "$NF)}'
#        	    	#''')
#        	    	stdin, stdout, stderr, status = tc.call('cd '+str(backup_dir)+';ls -gGhHrtl --full-time '+str(file_name))
#        	    	data=stdout.read()
#        	    	data=re.sub(" +", " ", data)
#        	    	res=data.split(' ')
#			#isDebug = True 
#			isDebug = False 
#        	    	try:
#        	        	b_time=res[3]+' '+res[4].split('.')[0]
#        	        	b_size=res[2]
#        	        	b_name=res[-1].strip()
#				if isDebug:
#        	        		print host,'\033[1;31;40m',backup_name,'\033[0m',b_time,'\033[1;36;40m',b_size,'\033[0m',b_name,'\033[1;34;40m',backup_dir,'\033[0m'
#        	    	except:
#        	        	b_time=''
#        	        	b_size=''
#        	        	b_name=''
#				if isDebug:
#        	        		print host,'\033[1;31;40m',backup_name,'\033[0m','\033[1;37;41m','warning!!','\033[0m'
##\			if not b_size:
#				sql = "update `check_backup` set `size`=' ' where id="+str(back_id)+" limit 1"
#			else:
#				sql = "update `check_backup` set `size`='"+b_size+"' where id="+str(back_id)+" limit 1"
#			cursor.execute(sql)
#        	    	list=[host+','+backup_name+','+b_time+','+b_size+','+b_name+','+backup_dir]
#        	    	result.append(list)
#        		stdout.close()
#        		stdin.close()
        	tc.close() 
#if is_auto:
#	content=toHtml(result)
#	sub="服务器备份每日统计("+str(Y)+'-'+str(m)+'-'+str(d)+")"
#	send_mail(mailto_list,sub,content)
#else:
#	print json.dumps('suc!')
#if len(err_result) > 0:
#	err_sub = "备件检查存在错误("+str(Y)+'-'+str(m)+'-'+str(d)+")"
#	err_content = toErrHtml(err_result)
#	#print err_content
#	send_mail(mailto_list, err_sub, err_content)
	
