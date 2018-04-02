#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import paramiko
class sshconnet(object):
	def __init__(self,host,port,name,pkey):
		self.host=host
		self.port=port
		self.name=name
		self.pkey=pkey
		self.ssh=paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(self.host, self.port,self.name,self.pkey)
	def ifconfig(self):
		stdin,stdout,stderr=self.ssh.exec_command('ifconfig')
		res_out = stdout.read()
		print(res_out.decode())
#		self.ssh.close()
	def ls(self):
		stdin,stdout,stderr=self.ssh.exec_command('ls -l')
		res_out = stdout.read()
		print(res_out.decode())
#		self.ssh.close()
test=sshconnet('192.168.3.217','22','root','/root/.ssh/id_rsa')
test.ifconfig()
test.ls()
