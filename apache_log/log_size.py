#!/usr/bin/env python
#coding=utf-8
#获取apache日志大小，并入库

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


def get_log_size(host,port,user,keyfile,*args):
    command = "LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;ps aux|grep -i [c]ronolog|awk '{if ($12==\"-S\") print $14;else print $12}'"
    cronoinfo = ssh_info(host,port,user,keyfile,command)
    print cronoinfo
    if cronoinfo is None:
	return None
    cronoinfo = cronoinfo.split('\n')
    sizecommand = "LANG=en_US.UTF-8; export LANG; LC_ALL=en_US.UTF-8;export LC_ALL;ls -al "
    tmp = {}
    cronnum = 0
    for info in cronoinfo:
	print info
	logdir = os.path.dirname(info)
    	m = re.match( logdir + "/(.*?access[._-])(.*?)$",info)
    	if m:
	    #print 'cronolog is matched'
	    cronnum += 1
	    domain = m.group(1)
	    datetype = m.group(2)
	    #print logdir + '/' + domain + datetype
	    if len(args) >0:
		owndate = args[0]
	    else:
		owndate = datetime.now() - timedelta(days=1)
	    print owndate
	    filename = logdir + '/' + domain + owndate.strftime(datetype)
	    print filename
	    sizecommand = sizecommand + filename + ' '
	    tmp[filename] = 0
    if cronnum == 0:
	return None
    sizecommand = sizecommand + "|awk '{print $9,$5}'"
    #print sizecommand
    filesize = ssh_info(host,port,user,keyfile,sizecommand)
    if filesize is None:
	return None
    filesize = filesize.split('\n')
    filesize = [file for file in filesize if file]
    for file in filesize:
	fileinfo = file.split(' ')
	tmp[fileinfo[0]] = fileinfo[1]
    filesize = tmp
    return filesize 


def domainToHtml(domaindict):
    #把dict转换成对应的html
    yestday = datetime.now() - timedelta(days=1)
    html = ""
    html += "<table width=\"650\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\">"
    html += "<th>" + "服务器地址" +"</th>" + "<th>" +  "域名" + "</th>" + "<th>"+  "创建时间" + "</th></tr>" 
    #html += "<tr style=\"text-align:center;\">"
    for ip,domainlist in domaindict.items() :
	#print html
        html += "<tr>"
	html += "<td  rowspan=\"" + str(len(domainlist)) + "\">" + ip + "</td>"
	for domain in domainlist:
	    print domain
	    print yestday
	    if domain[1].strftime('%Y-%m-%d') == yestday.strftime('%Y-%m-%d'):
		print 'yestday'
	        html += "<td bgcolor=\"red\">" + domain[0] + "</td>" + "<td>" + domain[1].strftime('%Y-%m-%d') + "</td>" + "</tr>" + "<tr>"
	    else:
	        html += "<td>" + domain[0] + "</td>" + "<td>" + domain[1].strftime('%Y-%m-%d') + "</td>" + "</tr>" + "<tr>"
	html += "</tr>"
    html += "</table>"
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
	    worksheet.write(row,col,client[0],merge_format)
	    col += 1
	    worksheet.write(row,col,client[1].strftime('%Y-%m-%d'),merge_format)
	    row += 1
	row = nextIProw +1
    workbook.close()    


def infoToHtml(domaindict,type):
    #把dict转换成对应的html
    html = ""
    if type == "new":
	html += "新建域名信息"
    else:
	html += "删除域名信息"
    html += "<table width=\"650\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\">"
    html += "<th>" + "服务器地址" +"</th>" + "<th>" +  "域名" + "</th>" + "</tr>" 
    #html += "<tr style=\"text-align:center;\">"
    for ip,domainlist in domaindict.items():
	#print html
        html += "<tr>"
	html += "<td  rowspan=\"" + str(len(domainlist)) + "\">" + ip + "</td>"
	for domain in domainlist:
	    print domain
	    html += "<td>" + domain + "</td>" + "</tr>" + "<tr>"
	html += "</tr>"
    html += "</table>"
    return html


class FuckDb():
    '''mysql数据库操作类'''
    def __init__(self,host,user,passwd,dbname,unix_socket):
	self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname, unix_socket=unix_socket)
	self.cursor = self.db.cursor()
	self.create_db()

    def create_db(self):
        sql = """CREATE TABLE APACHELOG (
	     SIP CHAR(20) NOT NULL,
	     DOMAIN CHAR(50),
	     FILENAME CHAR(100),
	     FILESIZE INT,
	     LOGDATE	DATE,
	     UNIQUE KEY INDEX_LOG_INFO(SIP,FILENAME,LOGDATE)
	  )"""
	try:
            self.cursor.execute(sql)
	except MySQLdb.Error as err:
	    if err.args[0]  == 1050:
		print err.args[1]
	sql = """CREATE TABLE DOMAIN (
		SIP CHAR(20) NOT NULL,
		DOMAIN CHAR(50),
		CTIME DATE,
		LTIME DATE,
		UNIQUE KEY INDEX_DOMAIN_INFO(SIP,DOMAIN))"""
	#CTIME Create time
	#LTIME Last check time
	try:
	    self.cursor.execute(sql)
	except MySQLdb.Error as err:
	    if err.args[0] == 1050:
		print err.args[1]
        self.db.commit()

    def add_info(self,IPlist,*args):
	#向数据库中插入数据
        for ip in IPlist:
            hostport = ip.split(":")
            host = hostport[0]
            port = int(hostport[1])
            print host+ ':'+ str(port)
            # 检查主机信息
            if host == "118.26.229.9":
	        keyfile = "/root/apache_log/9.ini"
	    else:
            # 检查主机信息
                keyfile = "/root/.ssh/id_rsa"
            user = "root"

            filesize = get_log_size(host,port,user,keyfile,*args)
            if filesize is None:
	        continue
            self.insert_db(host,filesize,*args)


    def insert_db(self,sip,filesize,*args):
	yestday = datetime.now() - timedelta(days=1)
	yestday = yestday.strftime('%Y-%m-%d')
   	if len(args) >0:
            owndate = args[0]
        else:
            owndate = datetime.now() - timedelta(days=1)

	for file,size in filesize.items():
	    logdir = os.path.dirname(file)
	    m = re.match( logdir + "/(.*?)[._-]access[._-](.*?)$",file)
	    if m:
		domain = m.group(1)
	        print 'domain is:' + domain
	    	try:
		    self.cursor.execute("INSERT INTO DOMAIN (SIP,DOMAIN,CTIME,LTIME) VALUES (%s,%s,%s,%s)", (sip,domain,yestday,yestday))
		    self.db.commit()
		except MySQLdb.Error as err:
		    if err.args[0] == 1062:
			print err.args[1]
			self.cursor.execute("UPDATE DOMAIN SET LTIME=%s WHERE SIP=%s AND DOMAIN=%s",(yestday,sip,domain))
			self.db.commit()
	    	try:
	            self.cursor.execute("INSERT INTO APACHELOG (SIP,DOMAIN,FILENAME,FILESIZE,LOGDATE) VALUES (%s,%s,%s,%s,%s)",(sip,domain,file,size,owndate))
	            self.db.commit()
	    	except MySQLdb.Error as err:
	            if err.args[0] == 1062:
		        print err.args[1]

    def get_domain(self):
	self.cursor.execute("SELECT DISTINCT(SIP) FROM DOMAIN")
	iplist = self.cursor.fetchall()
	iplist = [ip[0] for ip in iplist]
	print iplist
	domainlist = {}
	for ip in iplist:
	    self.cursor.execute("SELECT DOMAIN,CTIME FROM DOMAIN WHERE SIP=%s",(ip,))
	    rows = self.cursor.fetchall()
	    rows = [row for row in rows]
	    domainlist[ip] = rows

	return domainlist

    def get_deldomain(self):
	'''获取删除domain信息'''
	yestday = datetime.now() - timedelta(days=2)
        yestday = yestday.strftime('%Y-%m-%d')
	self.cursor.execute("SELECT SIP,DOMAIN FROM DOMAIN WHERE LTIME=%s",(yestday,))
	rows = self.cursor.fetchall()
	domaindict = {}
	for row in rows:
	    print row
	    if row[0] in domaindict.keys():
		domaindict[row[0]].append(row[1])
	    else:
		domaindict[row[0]] = [row[1]]
	return domaindict
	
    def get_newdomain(self):
	'''获取新domain信息'''
	yestday = datetime.now() - timedelta(days=1)
	yestday = yestday.strftime('%Y-%m-%d')
	self.cursor.execute("SELECT SIP,DOMAIN FROM DOMAIN WHERE CTIME=%s",(yestday,))
	rows = self.cursor.fetchall()
	domaindict = {}
	for row in rows:
	    print row
	    if row[0] in domaindict.keys():
		domaindict[row[0]].append(row[1])
	    else:
		domaindict[row[0]] = [row[1]]
	return domaindict

def main(argv):
    global host
    global user
    global passwd
    global dbname
    global unix_socket
    global serverinfo
    global sendto
    db = FuckDb(host,user,passwd,dbname,unix_socket)
    
    IPlist = []
    with open('iplist.txt','rt') as f:
	for ip in f.readlines():
	    ip = ip.strip('\n')
	    if ip:
		IPlist.append(ip)
    #db.create_db()
    if argv[1] == "-u":
	print "update db info"
	if len(argv) > 2:
	    setdate = datetime.strptime(argv[2],'%Y-%m-%d')
	    db.add_info(IPlist,setdate)
	else:
	    db.add_info(IPlist)
    elif argv[1] == "-d":
	print "send domain info"
    	domainlist = db.get_domain()
    	domainhtml = domainToHtml(domainlist)
    	print domainhtml
	yestday = datetime.now() - timedelta(days=1)
	title = ["主机","域名","创建时间"]
	filename = 'xls/DOMAIN_INFO_' + yestday.strftime('%Y_%m_%d') + '.xlsx'
	writeToExcel(title,domainlist,filename)
	sendMail(yestday.strftime('%Y-%m-%d') + "域名信息", domainhtml, sendto, serverinfo,filename)
    elif argv[1] == "-di":
	print " domain change info"
	deldomain = db.get_deldomain()
	if len(deldomain) == 0:
	    print "There is no delete domain info"
	    html = ""
	else:
	    print "delete domain is:"
	    print deldomain
	    html = infoToHtml(deldomain,"del")
	newdomain = db.get_newdomain()
	if len(newdomain) == 0:
	    print "There is no new domain"
	else:
	    print "new domain is:"
	    print newdomain
	    html += infoToHtml(newdomain,"new")
	if len(html) <10 :
	    html = "昨日无域名修改信息"
	yestday = datetime.now() - timedelta(days=1)
	sendMail(yestday.strftime('%Y-%m-%d') + "域名信息", html, sendto, serverinfo)
    else:
	print '-d:发送domain信息（全部）'
	print '-u:昨天日志信息入库'
	print '-di:显示昨天删除或增加域名信息'
    return 0

if __name__=='__main__':
    host = "localhost"
    user = "monitor"
    passwd = "www.ci123.com"
    dbname = "monitordb"
    unix_socket = "/tmp/mysql.sock"
    serverinfo = {'mail_host':'smtp.163.com',
    		'mail_user':'ci123webserver@163.com',
    		'mail_pass':'ci123webserver12'}
    sendto = ['cjy@corp-ci.com']
    sys.exit(int(main(sys.argv)))
