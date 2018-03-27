#!/bin/env python
# -*- encoding: utf-8 -*-
import datetime
import time
import os
import sys
import xlwt
import xlrd
import smtplib
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import json
import os.path
import mimetypes
import email.MIMEImage
def txt2xls(xlsname):
    f = os.system("kubectl get namespaces")
    x = 0
    y = 0
    s = os.system("kubectl get svc -o wide --all-namespaces")
    a = 0
    b = 0
    p = os.system("kubectl get pods -o wide --all-namespaces")
    c = 0
    d = 0
    q = os.system("docker images -a")
    m = 0
    n = 0
    xls=xlwt.Workbook()
    sheet1 = xls.add_sheet('namespaces',cell_overwrite_ok=True)
    sheet2 = xls.add_sheet('svc',cell_overwrite_ok=True)
    sheet3 = xls.add_sheet('pods',cell_overwrite_ok=True)
    sheet4 = xls.add_sheet('images',cell_overwrite_ok=True)
    while True:
##########################  pods #######################
        linepod = p.readline()
        if not linepod:
            break
        for i in linepod.split():
            item=i.strip().decode('utf8')
            sheet3.write(c,d,item)
            d += 1
        c += 1
        d = 0
##########################   services  #################
    while True:
        linesvc = s.readline()
        if not linesvc:
            break
        for i in linesvc.split():
            item=i.strip().decode('utf8')
            sheet2.write(a,b,item)
            b += 1
        a += 1
        b = 0
#########################  namespaces #################
    while True:
        line = f.readline()
        if not line:
            break
        for i in line.split():
            item=i.strip().decode('utf8')
            sheet1.write(x,y,item)
            y += 1
        x += 1
        y = 0
######################## images  #####################
    while True:
        line = q.readline()
        if not line:
            break
        for i in line.split():
            item=i.strip().decode('utf8')
            sheet4.write(m,n,item)
            n += 1
        m += 1
        n = 0
    xls.save(xlsname+'.xls')
def sendmail(file_name):
        From = "发件人"
        To = "收件人"
        server = smtplib.SMTP("邮件服务器")
        server.login("grafana@ciurl.cn","")
        main_msg = email.MIMEMultipart.MIMEMultipart()

        text_msg = email.MIMEText.MIMEText("kubernetes 集群namespaces、services、pods信息报表 ",_charset="utf-8")
        main_msg.attach(text_msg)
        ctype,encoding = mimetypes.guess_type(file_name)
        if ctype is None or encoding is not None:
            ctype='application/octet-stream'
        maintype,subtype = ctype.split('/',1)
        file_msg=email.MIMEImage.MIMEImage(open(file_name,'rb').read(),subtype)
        print ctype,encoding
        basename = os.path.basename(file_name)
        file_msg.add_header('Content-Disposition','attachment', filename = basename)
        main_msg.attach(file_msg)

        main_msg['From'] = From
        main_msg['To'] = To
        main_msg['Subject'] = "kubernetes统计报表"
        main_msg['Date'] = email.Utils.formatdate( )

        fullText = main_msg.as_string( )
        try:
            server.sendmail(From, To, fullText)
        finally:
            server.quit()


if __name__ == "__main__":
	xlsname='report'
    txt2xls(xlsname)
	sendmail(xlsname + 'xls')
