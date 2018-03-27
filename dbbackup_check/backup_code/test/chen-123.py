#!/usr/bin python
#coding:utf-8

import paramiko
import sys

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

result=[]
err_result = {}

tc = NewClient()
tc.load_system_host_keys()
tc._policy = paramiko.AutoAddPolicy()
try:
	host = '192.168.0.112'
	key = '/opt/scripts/dbbackup_check/ci123dev'
	port = 29622
	user = 'ci123dev'
	print host,port,user,key
	tc.connect(host,port=29622, username='ci123dev',key_filename=key,timeout=10) #timeout为5秒
	print "ok"
except Exception as err:#链接超时或者错误 返回err continue
	print err
	err_result[host] = str(id)+"###"+str(err)


