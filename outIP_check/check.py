#!/usr/bin/python
#coding: utf-8
import requests,datetime,re,os,time
import sys
#reload(sys) 
#sys.setdefaultencoding('utf-8')
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
            ip = txt[txt.find("您现在的 IP：") + 14:txt.find("所在地理位置") - 14]
            return ip
            break
if __name__ == '__main__':
    ip=get_out_ip()
    print(ip)
