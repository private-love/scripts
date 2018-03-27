#!/usr/bin/env python
#coding=utf-8

import sys
import os
import subprocess
import re
from datetime import datetime
from datetime import timedelta
import MySQLdb
import paramiko
from sendEmail import sendMail
import xlsxwriter


reload(sys)
sys.setdefaultencoding('utf-8')


def ssh_info(host,port,user,keyfile,command):
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print command
	trytime = 0
	while True:
		if trytime < 3:
			try:
				print 'starting ssh connect'
				ssh.connect(host,port=int(port), username=user, key_filename=keyfile, timeout=10)
				ip_stdin, ip_stdout, ip_stderr = ssh.exec_command(command,timeout=10)
				break
			except paramiko.ssh_exception.SSHException as e:
				print e
				trytime += 1
				continue
			except paramiko.ssh_exception.AuthenticationException as e:
				print e
			except:
				print 'error'
				trytime += 1
				continue
		else:
			return None
	data = ip_stdout.read()
	print 'data is:' + data
	if not data :
		return None
	ssh.close()
	return data


if __name__ == '__main__':
	host = '180.96.7.115'
	port = '29622'
	user = 'root'
	keyfile = '/root/.ssh/id_rsa'
	command = 'ssh 192.168.1.66 -p 29622 ' + "'cd /opt/ci123/backup/nbg;ls -gGHrtl --full-time dbnbg170206.sql.gz'"
	info = ssh_info(host,port,user,keyfile,command)
	print info
