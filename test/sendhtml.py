#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests,datetime,re,os
import smtplib,email.MIMEText,email.MIMEMultipart
def sendmail(text):
    checktime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    From = "grafana@ciurl.cn"
    To = "wangluxin@corp-ci.com"
    server = smtplib.SMTP("exmail.ciurl.cn")
    server.login("grafana@ciurl.cn","asbg123a2")
    main_msg = email.MIMEMultipart.MIMEMultipart()
#    text_msg = email.MIMEText.MIMEText("www"+' '.join(text).encode("utf-8"),_charset="utf-8")
    text_msg = email.MIMEText.MIMEText(text,_subtype='html',_charset="utf-8")
    main_msg.attach(text_msg)
    main_msg['From'] = From
    main_msg['To'] = To
    main_msg['Subject'] = "数据库备份恢复检测 " + checktime
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string( )
    try:
        server.sendmail(From, To.split(","), fullText)
    finally:
        server.quit()
if __name__ == '__main__':
    sendmail("text")