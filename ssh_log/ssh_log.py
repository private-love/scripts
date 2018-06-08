#!/usr/bin/env python
#coding=utf-8

import sys
import os
import re
import json
from time import sleep
from datetime import datetime
from datetime import timedelta
import paramiko
import requests
import xlsxwriter
from sendEmail import sendMail

reload(sys)
sys.setdefaultencoding('utf-8')


def find_addr(ip):
    #通过新浪IP API查询ip所在地，不在南京就返回True
    global whiteiplist
    if ip not in whiteiplist:
	print ip + 'NOT in IP LIST'
    	url = "http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js&ip="
    	trytime = 0
    	while True:
	    try:
	    	r = requests.get(url + ip,timeout=10)
	    	break
	    except:
	    	if trytime < 3:
	            sleep(2)
		    trytime += 1
	            continue
	        else:
		    return False
    	m = re.search('({.*});$',r.text)
    	if m:
	    print m.group(1)
	    urlinfo = json.loads(m.group(1))
	    if urlinfo['ret'] == -1:
		return False
	    print urlinfo[u'province'].encode('utf-8')
	    print urlinfo[u'city'].encode('utf-8')
	    if urlinfo[u'city'].encode('utf-8') != '南京':
	        print '地址不在南京'
	        return True
            else:
	        return False
    else:
	return False

def refuseToHtml(info):
    #refuse信息转换成html格式
    html = ""
    html += "<table width=\"650\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\">"
    html += "<th>" + "服务器地址" +"</th>" +  "<th>"+  "IP地址" + "</th>" 
    html += "<th>" + "时间" + "</th>"  + "</tr>"
    #html += "<tr style=\"text-align:center;\">"
    if not info:
	exit()
    for host,refuselist in info.items() :
	#print html
        html += "<tr>"
	html += "<td  rowspan=\"" + str(len(refuselist)) + "\">" + host + "</td>"
	for refuse in refuselist:
	    if refuse:
		notInNJ = find_addr(refuse[3])
		if notInNJ is True:
		    html += "<td bgcolor=\"red\">" + refuse[3] + "</td>" + "<td>" + refuse[2] + "</td>" + "</tr>" + "<tr>"
		else:
	            html += "<td>" + refuse[3] + "</td>" + "<td>" + refuse[2]  + "</td>" + "</tr>" + "<tr>"
	html += "</tr>"
    html += "</table>"
    #print html
    return html


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
	    if find_addr(client[3]):
	    	worksheet.write(row,col,client[3],warn_format)
	    else:
	    	worksheet.write(row,col,client[3],merge_format)
	    col += 1
	    worksheet.write(row,col,client[2],merge_format)	
	    row += 1
	row = nextIProw +1
    workbook.close()    


def ssh_info(host,port,user,keyfile):
    global command
    if host != '192.168.0.254':
	return
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    trytime = 0
    while True:
    	try:
	    print 'starting ssh connect'
	    ssh.connect(host,port=port, username=user, key_filename=keyfile, timeout=10)
    	    ip_stdin, ip_stdout, ip_stderr = ssh.exec_command(command)
	    break
        except:
	    if trytime >= 3:
		return None
	    else:
	    	sleep(2)
		trytime += 1
	    	continue
    refuselist = re.split('\n',ip_stdout.read())
    refuselist = [ refuse for refuse in refuselist if refuse]
    refuselist = [re.split('[ ]+',refuse) for refuse in refuselist ]
    tmplist = []
    for refuse in refuselist:
	tmplist.append([refuse[0],refuse[1],refuse[2],refuse[8]])
    refuselist = tmplist
    if len(refuselist) != 0:
	print refuselist
	return refuselist
    else:
	return None


def get_ssh_info():
    IPlist = []
    with open('iplist.txt','rt') as f:
	for ip in f.readlines():
	    ip = ip.strip('\n')
	    if ip:
		IPlist.append(ip)
    denydict = {}
    for ip in IPlist:
        hostport = ip.split(":")
        host = hostport[0]
        port = int(hostport[1])
        print host+ ':'+ str(port)
        # 检查主机信息
        if host == "xxx":
	    key = "xxx"
	else:
        # 检查主机信息
            key = "/root/.ssh/id_rsa"
        user = "root"
        refuselist = ssh_info(host,port,user,key)
	if refuselist is not None:
	    denydict[host] = refuselist
    return denydict


def main():
    denydict = get_ssh_info()
    for ip,refuselist in denydict.items():
	print ip
	print refuselist
    refusehtml = refuseToHtml(denydict)
    print refusehtml
    title = ['服务器地址','用户IP','时间']
    lasthour = datetime.now() - timedelta(hours=1)
    filename = 'xls/ssh_refused_' + lasthour.strftime('%Y-%m-%d-%H') + '.xlsx' 
    writeToExcel(title,denydict,filename)
    sendMail('ssh拒绝登录信息',refusehtml,sendto,serverinfo,filename)

if __name__ == '__main__':
    serverinfo = {'mail_host':'smtp.163.com',
    		'mail_user':'xxx',
    		'mail_pass':'xxx'}
    sendto = ['xxx']

    whiteiplist = []
    with open('whiteIPlist.txt','rt') as f:
        for ip in f.readlines():
	    whiteiplist.append(ip.strip('\n'))

    lasthour = datetime.now() - timedelta(hours=1)
    MON = lasthour.strftime('%b')
    DAY = lasthour.strftime('%d')
    m = re.match('0(\d)',DAY)
    if m:
        DAY = m.group(1)
    lhour = lasthour.strftime('%H')
    command = "LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;cat /var/log/secure | " + "grep -E \"" + MON + "[ ]+" + DAY + "[ ]+" + lhour +  ":[0-5][0-9]:[0-5][0-9]\"" + "|grep -i [r]efused"
    #command = "LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;cat /var/log/secure | " + "grep -E \"" + MON + "[ ]+15[ ]+21:[0-5][0-9]:[0-5][0-9]\"" + "|grep -i [r]efused"
#    command = "last|grep -E 'May[ ]11[ ]09|May[ ][ ]11[ ]09'  last|grep still"
    print command
    main()  
