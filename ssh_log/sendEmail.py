#!/usr/bin/env python
#coding=utf-8

import os
import smtplib
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


def sendMail(subject, content, to_list,serverinfo, *attachmentFiles):
    '''发送带附件的邮件'''
    me = serverinfo['mail_user']		  
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
	    attachfile.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachmentFile))
	    msg.attach(attachfile)
    else:
	msg.attach(MIMEText(content, 'html', 'utf-8'))
    try:
	mailServer = smtplib.SMTP()
	#mailServer.starttls()
	mailServer.set_debuglevel(1)
	mailServer.connect(serverinfo['mail_host'],25)
	mailServer.login(serverinfo['mail_user'],serverinfo['mail_pass'])
	mailServer.sendmail(me, to_list, msg.as_string()) 
	mailServer.close()
	return True
    except Exception, e:
	print str(e)
	return False

if __name__=='__main__':
    pass
