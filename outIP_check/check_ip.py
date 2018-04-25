#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests,datetime,re,os,time
import sys
from bs4 import BeautifulSoup
import smtplib,email.MIMEText,email.MIMEMultipart
reload(sys) 
sys.setdefaultencoding('utf-8')
def get_out_ip(url=r'https://ip.cn/'):
    headers = { 'Accept':'text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Connection':'keep-alive',
                'Cookie':'__cfduid=d5eee4fadab7de55bfb36b5fc773aa2f51524618140; UM_distinctid=162fa52a1103c9-0813fca5a5a3528-12676c4a-1fa400-162fa52a111208; CNZZDATA123770=cnzz_eid%3D996372412-1524612947-%26ntime%3D1524612947',
                'Host':'ip.cn',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0' }
    for i in range(1,11):
        try:
            r = requests.get(url,headers=headers,timeout=10)
        except requests.exceptions.ConnectionError:
            print('网站限制访问，请检查头信息')
            time.sleep(10)
        else:
            txt = r.text
#            print txt
            ip = txt[txt.find("您现在的 IP：") + 14:txt.find("所在地理位置") - 14]
            return ip
            break
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
#    ip=get_out_ip()
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
    ip=get_out_ip()
    print(ip)
    iplist=[];iplist.append(ip)
    check(iplist)
