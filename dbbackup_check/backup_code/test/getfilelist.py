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
#mailto_list=["cjy@corp-ci.com"]
mailto_list=["wuwanli@corp-ci.com"]
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

class NewClient(paramiko.SSHClient):
    def call(self, command, bufsize=-1):
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        status = chan.recv_exit_status()
        return stdin, stdout, stderr, status
        
result={}
err_result = {} 
if __name__ == '__main__':
	if len(sys.argv) < 6:
		result['err'] = "参数错误"
		print json.dumps(result)
		sys.exit()
	host = str(sys.argv[1])
	port = int(sys.argv[2])
	user = str(sys.argv[3])
	key = str(sys.argv[4])
	path = str(sys.argv[5])
	if len(sys.argv) > 6:
		passwd = sys.argv[6]
	else:
		passwd = ''
	tc = NewClient()
	tc.load_system_host_keys()
	tc._policy = paramiko.AutoAddPolicy()
	try:
		key = '/opt/scripts/dbbackup_check/'+key
		tc.connect(host, port=port, username=user, password=passwd, key_filename=key, timeout=10)
	except Exception as err:
		result['err'] = str(err)
		print json.dumps(result)
		sys.exit()
        stdin, stdout, stderr, status = tc.call('cd '+str(path)+';ls -gGhHrtl --full-time ')
	err = stderr.read()
	if err:
		result['err'] = str(err)
		print json.dumps(result)
		sys.exit()
	out =[] 
	result['size'] = 0
        data=stdout.read()
	data = re.sub(" +", " ", data)
	temp = data.split('\n')
	for item in temp:
		if item[0:1] == '-':
			result['size'] += 1 
			itemres = item.split(' ')
			item_out = {}
			item_out['filename'] = itemres[6]
			item_out['size'] = itemres[2]
			out.append(item_out)
	result['out'] = out 
	print json.dumps(result)
        stdout.close()
        stdin.close()
        tc.close() 
