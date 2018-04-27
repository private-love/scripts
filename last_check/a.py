#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import paramiko
import sys
import string
import xlsxwriter

def get_last_info():
	command=subprocess.call('ls -l',shell =True)
	return command

def ssh_info(host,port,user,keyfile,command):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print 'starting ssh connect'
        ssh.connect(host,port=port, username=user, key_filename=keyfile, timeout=10)
        ip_stdin, ip_stdout, ip_stderr = ssh.exec_command(command)
    except paramiko.ssh_exception.SSHException as e:
        print e
        return None
    except:
        print 'error'
        return None
    else:
        data = ip_stdout.read()
        ssh.close()
	#print data
        return data

def writeToExcel(title,data,filename):
    '''写入excel'''
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0,len(title)-1,24)
    merge_format = workbook.add_format({'align': 'center','valign': 'vcenter','border': 1})
    warn_format = workbook.add_format({'align': 'center','valign': 'vcenter','border': 1,'bg_color':'red'})
    row = 0
    col = 0
    for name in title:
        worksheet.write(row,col,name,merge_format)
        col += 1
    row = 1
    for hostip,info in data.items():
        #col = 0
        nextIProw = row + len(info)-1
        if row == nextIProw:
            worksheet.write(row,0,hostip,merge_format)
        else:
            worksheet.merge_range(row,0,nextIProw,0,hostip,merge_format)
        for client in info:
            col = 1
            worksheet.write(row,col,client[0],merge_format)
            col += 1
            if find_addr(client[2]):
                worksheet.write(row,col,client[2],warn_format)
            else:
                worksheet.write(row,col,client[2],merge_format)
            col += 1
            if datetime.strptime('00:00','%H:%M') < datetime.strptime(client[6],'%H:%M') < datetime.strptime('07:00','%H:%M'):
                worksheet.write(row,col,client[6],warn_format)
	    else:
                worksheet.write(row,col,client[2],merge_format)
            col += 1
            worksheet.write(row,col,client[8],merge_format)
            col += 1
            worksheet.write(row,col,client[9],merge_format)
            row += 1
        row = nextIProw +1
    workbook.close()
	
#get_last_info()
if __name__ == '__main__':
	ssh_info("221.231.140.244",29622,"root","/root/.ssh/id_rsa","mkdir /root/jr/testjr")
	ssh_info("221.231.140.244",29622,"root","/root/.ssh/id_rsa","rsync -avr /root/jr/testjr /root/jr/testjr2")
	#iplist=/root/jr/sh/ip.ini
	#for i in iplist:
#	for i in open("/opt/scripts/last_check/iplist.txt"):
#	#print i
#		i = i.strip('\n')
#		b=i.split(":")
#		print b[0],b[1]
#		c=string.atoi(b[1])
#	IPlist = []
#	with open('iplist.txt','rt') as f:
#		for ip in f.readlines():
#    			ip = ip.strip('\n')
#    			if ip:
#        			IPlist.append(ip)
##	print IPlist
##	print len(IPlist)
#	for i in IPlist:
#               b=i.split(":")
#               print b[0],b[1]
#               c=string.atoi(b[1])
#	       ssh_info(b[0],c,"root","/root/.ssh/id_rsa","ls")
#	#    print c
#	#jr=cmd(b[0],c,"root","/root/.ssh/id_rsa","w")
#	#print jr
#       	#ssh_info(b[0],c,"root","/root/.ssh/id_rsa","ls")

