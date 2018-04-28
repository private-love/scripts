#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests,datetime,re,os,time
import smtplib,email.MIMEText,email.MIMEMultipart
def sendmail(text):
    print(text)
    From = "grafana@ciurl.cn"
    To = "wangluxin@corp-ci.com"
    server = smtplib.SMTP("exmail.ciurl.cn:10025")
    server.login("grafana@ciurl.cn","asbg123a2")
    main_msg = email.MIMEMultipart.MIMEMultipart()
#    text_msg = email.MIMEText.MIMEText("www"+' '.join(text).encode("utf-8"),_charset="utf-8")
    text_msg = email.MIMEText.MIMEText(text,_charset="utf-8")
    main_msg.attach(text_msg)
    main_msg['From'] = From
    main_msg['To'] = To
    main_msg['Subject'] = "aliyun_disk_check"
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string( )
    try:
        server.sendmail(From, To, fullText)
    finally:
        server.quit()
if __name__ == '__main__':
    sendmail("text")