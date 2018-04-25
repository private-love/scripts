#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import re
import json
import smtplib
from datetime import datetime
from datetime import timedelta
from email.mime.text import MIMEText
import sys,os
from collections import OrderedDict
from datetime import datetime
#import global_functions as func
import paramiko
import requests
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase  
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64
from email.mime.text import MIMEText
from email.message import Message
from email.header import Header
from email.mime.application import MIMEApplication
import xlsxwriter

reload(sys)
sys.setdefaultencoding('utf-8')

def get_last_info():
    shell_command = "LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;last|grep -E \"$(date '+%a %b')[ ]+$(date|awk '{print $3}')\""
    child = subprocess.Popen(shell_command,shell=True,stdout=subprocess.PIPE)
    logininfo = child.stdout.read().decode('utf-8')
    loginlist = re.split('\n',logininfo)
    loginlist = [ login for login in loginlist if login]
    loginlist = [re.split('[ ]+',login) for login in loginlist ]
    return loginlist

def get_login_num(loginlist):
    '''获取各时间段登陆用户数，已经去掉重复IP'''
    global timelist
    userdict = OrderedDict()
    for time in timelist:
        lnum = 0
        iplist = []
        userlist = []
	info = []
        for userinfo in loginlist:
            m = re.match(time +':[0-5][0-9]',userinfo[6])
            if m:
                if (userinfo[2] not in iplist) or (userinfo[0] not in userlist):
                    lnum+=1
                    userlist.append(userinfo[0])
                    iplist.append(userinfo[2])
		    info.append([userinfo[0],userinfo[2]])
        userdict[time]=info
    print userdict
    return userdict

def still_login(loginlist):
    '''获取仍然在线用户，去掉重复用户'''
    global timelist
    iplist = []
    logindict = {}
    for user in loginlist:
        m = re.match('still',user[7])
        if m:
            if user[2] not in iplist:
                iplist.append(user[2])
                logindict[user[2]] = [user[0],user[6]]
                # print('用户名：' + user[0]  + '用户IP:' + user[2] + '在' + user[6] + '登陆，' + '现仍然在线')
    return logindict

def most_login(loginlist):
    '''获取一天中登陆数最多的用户，统计IP'''
    global timelist
    ipdict = {}
    for user in loginlist:
        if user[2] in ipdict.keys():
            ipdict[user[2]]+=1
        else:
            ipdict[user[2]] =1
    return ipdict


def get_sec_info():
    child = subprocess.Popen("LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;grep -i \"authentication failure\" /var/log/secure|grep -E \"$(date '+%b')[ ]+$(date|awk '{print $3}')\"",shell=True,stdout=subprocess.PIPE)
    secinfo = child.stdout.read().decode('utf-8')
    secinfo = re.split('\n',secinfo)
    Mon = subprocess.Popen("LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;date '+%b'",shell=True,stdout=subprocess.PIPE).stdout.read().decode('utf-8').strip('\n')
    Day = subprocess.Popen("LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;date|awk '{print $3}'",shell=True,stdout=subprocess.PIPE).stdout.read().decode('utf-8').strip('\n')
    print Mon 
    print Day
    Date = Mon+ '[ ]+' + Day
    errlogin = []
    for info in secinfo:
	m = re.search('([0-2][0-9]:[0-5][0-9]:[0-5][0-9]).*user=(.*?)$',info)
	if m:
	    print 'match'
	    print m.group(1) +  m.group(2)
	    logintime = m.group(1)
	    loginuser = m.group(2)
	    errlogin.append([m.group(1),m.group(2)])
    print errlogin


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
    	return data

def lastToHtml(info):
    #last信息转换成html格式
    html = ""
    html += "<table width=\"650\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\">"
    html += "<th>" + "服务器地址" +"</th>" + "<th>" +  "用户名" + "</th>" + "<th>"+  "IP地址" + "</th>" 
    html += "<th>" + "登录时间" + "</th>" + "<th>""下线时间" "</th>" + "<th>" + "持续时间" +"</th>" + "</tr>"
    #html += "<tr style=\"text-align:center;\">"
    if not info:
	exit()
    for host,loginlist in info.items() :
	#print html
        html += "<tr>"
	html += "<td  rowspan=\"" + str(len(loginlist)) + "\">" + host + "</td>"
	for login in loginlist:
	    #print html
	    #print login
	    if login:
		if login[0] != "wtmp":
		    notInNJ = find_addr(login[2])
		    if notInNJ is True:
			if datetime.strptime('00:00','%H:%M') < datetime.strptime(login[6],'%H:%M') < datetime.strptime('07:00','%H:%M'):
	                    html += "<td>" + login[0] + "</td>" + "<td bgcolor=\"red\">" + login[2] + "</td>" + "<td bgcolor=\"red\">" + login[6] + "</td>" + "<td>" + login[8] + "</td>" + "<td>" + login[9] + "</td>" + "</tr>" + "<tr>"
	                else:
			    html += "<td>" + login[0] + "</td>" + "<td bgcolor=\"red\">" + login[2] + "</td>" + "<td>" + login[6] + "</td>" + "<td>" + login[8] + "</td>" + "<td>" + login[9] + "</td>" + "</tr>" + "<tr>"
		    else:
			if datetime.strptime('00:00','%H:%M') < datetime.strptime(login[6],'%H:%M') < datetime.strptime('07:00','%H:%M'):
	                    html += "<td>" + login[0] + "</td>" + "<td>" + login[2] + "</td>" + "<td bgcolor=\"red\">" + login[6] + "</td>" + "<td>" + login[8] + "</td>" + "<td>" + login[9] + "</td>" + "</tr>" + "<tr>"
	                else:
	                    html += "<td>" + login[0] + "</td>" + "<td>" + login[2]  + "</td>" + "<td>" + login[6] + "</td>" + "<td>" + login[8] + "</td>" + "<td>" + login[9] + "</td>" + "</tr>" + "<tr>"
	html += "</tr>"
    html += "</table>"
    #print html
    return html


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


def getLastInfo(type):
    '''轮训所有服务器，获取对应login登录信息'''
    global commandlist
    if type == 'dlast':
        command = commandlist['dlast']
    elif type == 'last':
        command = commandlist['last']

    logindict = {}
    for ip in IPlist:
        hostport = ip.split(":")
        host = hostport[0]
        port = int(hostport[1])
        print host+ ':'+ str(port)
	if host == "xxx":
	    key = "xxx"
	else:
        # 检查主机信息
            key = "/root/.ssh/id_rsa"
        user = "root"
	info = ssh_info(host,port,user,key,command)
	if info is None:
	    print host + ' ssh connect error..continue next ssh'
	    continue
        if type == "last" or type == "dlast":
            loginlist = re.split('\n',info)
            loginlist = [ login for login in loginlist if login]
            loginlist = [re.split('[ ]+',login) for login in loginlist ]
            loginlist = [login for login in loginlist if login[0]!='wtmp']
            if loginlist:
                print loginlist
                logindict[host] = loginlist
            #elif type == "auth":
                #auth fail相关处理
    return logindict


def sendMail(subject, content, to_list, *attachmentFiles):
    '''发送带附件的邮件'''
    global mail_user
    me = mail_user		  
    msg = MIMEMultipart()
    msg['From'] = me
    if len(to_list)>1:
        msg['To'] = ";".join(to_list)
    else:
	msg['To'] = to_list[0]
    msg['Subject'] = Header(subject,'utf-8')

    if len(attachmentFiles) != 0:
    	print '存在附件'
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        for attachmentFile in attachmentFiles:
	    attachfile = MIMEApplication(open(attachmentFile,'rb').read())
	    attachfile.add_header('Content-Disposition', 'attachment', filename=attachmentFile)
	    msg.attach(attachfile)
    else:
	msg.attach(MIMEText(content, 'html', 'utf-8'))
    try:
	mailServer = smtplib.SMTP()
	#mailServer.starttls()
	mailServer.set_debuglevel(1)
	mailServer.connect(mail_host,25)
	mailServer.login(mail_user,mail_pass)
	mailServer.sendmail(me, to_list, msg.as_string()) 
	mailServer.close()
	return True
    except Exception, e:
	print str(e)
	return False

if __name__ == '__main__':
    mail_host="smtp.163.com"
    mail_user="xxx"
    mail_pass="xxx"

    timelist = ['00','01','02','03','04','05','06','07','08','09','10','11','12',
                '13','14','15','16','17','18','19','20','21','22','23']
    whiteiplist = []
    with open('whiteIPlist.txt','rt') as f:
        for ip in f.readlines():
	    whiteiplist.append(ip.strip('\n'))
    print whiteiplist
    print len(whiteiplist)
    IPlist = []
    with open('iplist.txt','rt') as f:
	for ip in f.readlines():
	    ip = ip.strip('\n')
	    if ip:
		IPlist.append(ip)
    print IPlist
    print len(IPlist)
    
    commandlist = {"last":"LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;last|grep -E \"$(date '+%a %b')[ ]+$(date|awk '{print $3}')[ ]+$(date '+%H' -d '-1 hours')\"",
		"dlast":"LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;last|grep -E \"$(date '+%a %b' -d '-1 days')[ ]+$(date -d '-1 days'|awk '{print $3}')\"",  
		"auth":"LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;grep -i \"authentication failure\" /var/log/secure|grep -E     \"$(date '+%b')[ ]+$(date|awk '{print $3}')\""}
    
    title = ['主机IP','用户名','登录IP','登录时间','下线时间','在线时长']	
    if len(sys.argv) >1 and sys.argv[1] == '-d':
	print '输出昨天信息'
	yestday = datetime.now() - timedelta(days=1)
	filename = 'xls/Login_info_' + yestday.strftime('%Y_%m_%d') + '.xlsx'
	logindict = getLastInfo('dlast')
	lastTable = lastToHtml(logindict)
    	print lastTable
    	writeToExcel(title,logindict,filename)
    	sendMail('昨天登陆数统计邮件-' + yestday.strftime('%Y_%m_%d'),lastTable,['cjy@corp-ci.com'],filename)
    elif len(sys.argv) > 1 and sys.argv[1] == '-h':
	print '按小时输出'
	lasthour = datetime.now() - timedelta(hours=1)
	filename = 'Login_info_' + lasthour.strftime('%Y_%m_%d_%H') + '.xlsx'
	logindict = getLastInfo('last')
    	lastTable = lastToHtml(logindict)
    	print lastTable
    	writeToExcel(title,logindict,filename)	
    	sendMail('登陆数统计邮件-' + lasthour.strftime('%Y_%m_%d_%H') + '时',lastTable,['cjy@corp-ci.com'],filename)
	os.remove(filename)
    else:
	print '''Usage:
		-d: 昨天
		-h：前一小时'''

