#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests,datetime,re
from bs4 import BeautifulSoup
import smtplib,email.MIMEText,email.MIMEMultipart
def get_out_ip(url):
    r = requests.get(url)
    txt = r.text
    ip = txt[txt.find("[") + 1: txt.find("]")]
    return ip
def get_real_url(url=r'http://www.ip138.com/'):
    r = requests.get(url)
    txt = r.text
    soup = BeautifulSoup(txt,"html.parser").iframe
    return soup["src"]
def sendmail(text):
    From = "grafana@ciurl.cn"
    To = "wangluxin@corp-ci.com"
    server = smtplib.SMTP("exmail.ciurl.cn")
    server.login("grafana@ciurl.cn","asbg123a2")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText("新增IP为："+' '.join(text).encode("utf-8"),_charset="utf-8")
    main_msg.attach(text_msg)
    main_msg['From'] = From
    main_msg['To'] = To
    main_msg['Subject'] = "aliyun外网IP发生变化，超出已掌握的IP_list"
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string( )
    try:
        server.sendmail(From, To, fullText)
    finally:
        server.quit()
def check(ipnew):
    checktime=datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    ip=get_out_ip(get_real_url())
    iplist=open("IP_list","a+")
    IPlist=[];IPnew=[];IPmail=[]
    for IP in iplist:
        line = IP.strip()
        b = re.split(r" +",line)
        IPlist.append(b[-1])
    if "101.132.46.255" not in IPlist:
        IPnew.append('101.132.46.255')
    if "101.132.238.25" not in IPlist:
        IPnew.append('101.132.238.25')
    iplist.close()
    for x in ipnew:
        if x not in IPlist and x not in IPnew:
            IPnew.append(x);IPmail.append(x)
        if IPnew:
            for i in IPnew:
               iplist=open("IP_list","a+")
               iplist.write(checktime+"  increase  "+i+'\n')
    if IPmail:
        sendmail(IPmail)
if __name__ == '__main__':
    checktime=datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    ip=get_out_ip(get_real_url())
    iplist=[];iplist.append(ip)
    check(iplist)
