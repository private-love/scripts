#!/bin/env python
#-*-coding:utf-8-*-

import os
import MySQLdb
import string
import sys
import ConfigParser
import smtplib
import math
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase  
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64
from email.mime.text import MIMEText
from email.message import Message
from email.header import Header
import xlsxwriter

reload(sys)
sys.setdefaultencoding('utf8')


def get_config(group,config_name):
	"""获取etc/config.ini配置项"""
        config = ConfigParser.ConfigParser()
        config.readfp(open('./etc/config.ini','rw'))
        config_value=config.get(group,config_name).strip(' ').strip('\'').strip('\"')
        return config_value

mail_host = get_config('mail_server','mail_host')
mail_user = get_config('mail_server','mail_user')
mail_pass = get_config('mail_server','mail_pass')
mail_postfix = get_config('mail_server','mail_postfix')
mailto_list_str = get_config('mail_server','mailto_list')
mailto_list = mailto_list_str.split(",")

idc_type = get_config('idc','idc_type')
key_path = get_config('key_info','key_path_file')
key_user = get_config('key_info','key_user')

def get_db_config():
	"""获取数据库配置信息并返回，供MySQL使用"""
	host = get_config('backup_db_server','host')
	port = get_config('backup_db_server','port')
	user = get_config('backup_db_server','user')
	passwd = get_config('backup_db_server','passwd')
	dbname = get_config('backup_db_server','dbname')
	dbconfig = {
		'host':host,
		'port':string.atoi(port),
		'user':user,
		'passwd':passwd,
		'db':dbname,
		'charset':'utf8'
	}
	return dbconfig

def send_mail(to_list,sub,content):
	'''
	to_list:发给谁
	sub:主题
    	content:内容
    	send_mail("xxxx@126.com","sub","content")
    	'''
    	me = mail_user
    	#me=mail_user+"<</span>"+mail_user+"@"+mail_postfix+">"
    	msg = MIMEText(content, 'html', 'utf-8')
    	msg['Subject'] = Header(sub,'utf-8')
    	#msg['From'] = Header(me,'utf-8')
    	msg['From'] = me
    	msg['To'] = ";".join(to_list)
    	try:
       		s = smtplib.SMTP()
        	s.connect(mail_host)
        	s.login(mail_user,mail_pass)
        	s.sendmail(me,to_list, msg.as_string())
        	s.close()
        	return True
    	except Exception, e:
        	print str(e)
        	return False

def sendMail(subject, content, to_list, *attachmentFilePaths):
	"""发送带附件的邮件""" 
	me = mail_user 
  
    	msg = MIMEMultipart()  
    	msg['From'] = me  
    	msg['To'] = ";".join(to_list)  
    	msg['Subject'] = subject  
    	msg.attach(MIMEText(content, 'html', 'utf-8'))  
  
    	for attachmentFilePath in attachmentFilePaths:  
        	msg.attach(getAttachment(attachmentFilePath))  
  
	try:
    		mailServer = smtplib.SMTP()
		mailServer.connect(mail_host)
		mailServer.login(mail_user,mail_pass)
		mailServer.sendmail(me, to_list, msg.as_string())  
    		mailServer.close()
		print('Sent email to %s' % ";".join(to_list))
		return True
	except Exception, e:
		print str(e)
		return False
	 
def getAttachment(attachmentFilePath):  
    	contentType, encoding = mimetypes.guess_type(attachmentFilePath)  
  
    	if contentType is None or encoding is not None:  
        	contentType = 'application/octet-stream'  
  
    	mainType, subType = contentType.split('/', 1)  
    	file = open(attachmentFilePath, 'rb')  
  
    	if mainType == 'text':  
        	attachment = MIMEText(file.read())  
    	elif mainType == 'message':  
        	attachment = email.message_from_file(file)  
    	elif mainType == 'image':  
        	attachment = MIMEImage(file.read(),_subType=subType)  
    	elif mainType == 'audio':  
        	attachment = MIMEAudio(file.read(),_subType=subType)  
    	else:  
        	attachment = MIMEBase(mainType, subType)  
    	attachment.set_payload(file.read())  
    	encode_base64(attachment)  
  
    	file.close()  
  
    	attachment.add_header('Content-Disposition', 'attachment',   filename=os.path.basename(attachmentFilePath))  
    	return attachment  

def toErrHtml(dict):
	"""备份检查错误，邮件html代码"""
        html = ""
        html += "<table width=\"600\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
        html += "<tr style=\"text-align:center;\"><td>服务器</td><td>原因</td></tr>"
        for key,value in dict.items():
                list = value.split('###')
                id = list[0]
                reason = list[1]
                html += "<tr align=\"justify\" >"
                html += "<td nowrap=\"nowrap\" style=\"padding:0px 10px;\">"
                html += "<a href=\"http://racktables.ci123.com/backup/backup_host_add.php?id="+id+"\" target=\"_blank\">"+str(key)+"</a>"
                html += "</td>"

                html += "<td nowrap=\"nowrap\" style=\"padding:0px 10px;\">"
                html += str(reason)
                html += "</td>"
                html += "</tr>"
        html += "</table>"
        return html

def toHtml(list,total_size_str):
	"""备份检查内容html邮件代码转换函数"""
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
	total_row = 0
	total_db = 0
    	for key in key_list:
        	data = dict[key]
        	n = len(data)
		total_row += 1
        	for d in data:
            		html += "<tr align=\"justify\" >"

            		if(count):
                		html += "<td nowrap=\"nowrap\" rowspan="+ str(n) +" style=\"padding:0px 10px;\">"
                		html += str(key)
                		html += "</td>"
                		count = False

            		iserror = not d[-2].strip(" ")
			total_db += 1
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
	if total_size_str :
		html += "<tr style=\"padding:0px 10px;height:30px;\"><td>备份概述</td><td colspan=\"5\">"+str(total_row)+"台服务器，"+str(total_db)+"个数据库实例，备份总量："+str(total_size_str)+"</td></tr>"

    	html += "</table>"
    	return html

def convertBytes(bytes,lst=['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']):
	"""
	将文件字节大小转换成可读性更高的单位
	"""
        i = int(math.floor(math.log(bytes, 1024)))
        if i >= len(lst):
        	i = len(lst) - 1
        return ('%.2f' + " " + lst[i]) % (bytes/math.pow(1024, i))
