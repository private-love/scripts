#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests,datetime,re,os,time,paramiko,multiprocessing
from sendmails import sendmail
def check():
    f=open('./iplist.txt','r')
    iplist=[];portlist=[]
    for ips in f:
        ip = ips.strip()
        if not ip.startswith ('#'):
            b = re.split(r":",ip)
            iplist.append(b[0])
            portlist.append(b[1])
    pronum=len(iplist)
    p = multiprocessing.Pool(processes=pronum)
    text=[]
    for i in range(len(iplist)):
        result = p.apply_async(sshcommend,args=(iplist[i],portlist[i],))
        text.append(result.get())
    allsizes = os.popen("df -Th|grep -Ev 'nfs|tmpfs|overlay|Filesystem'|awk '{print $(NF-1)}'|awk -F % '{print $1}'")
    sizes = os.popen("du -sh /var/log/|awk '{print $1}'")
    allsize = allsizes.read().strip()
    size = sizes.read().strip()
    if int(allsize) > asize:
        localtext = "192.168.83.47 : Disk Utilization more then 80% , now is :" + allsize + "% ; (and /var/log/ size is : " + size + ")"
        text.append(localtext)
    if text:
        text.sort()
    return text
    p.close()
    p.join()
def sshcommend(ipnum,portnum):
    private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ipnum, port=int(portnum), username='root', pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command("df -Th|grep -Ev 'nfs|tmpfs|overlay|Filesystem'|awk '{print $(NF-1)}'|awk -F % '{print $1}'")
    result=stdout.read()
    stdin, stdout, stderr = ssh.exec_command("du -sh /var/log/|awk '{print $1}'")
    results=stdout.read()
    ssh.close()
    allsize = result.strip()
    size = results.strip()
    if int(allsize) > asize:
       text = ipnum +" : Disk Utilization more then 80% , now is :" + allsize + "% ; (and /var/log/ size is : " + size + ")"
       return text
if __name__ == '__main__':
    asize = 80
    body = check()
    text=''
    if body:
        for i in body:
            if str(i) != "None":
                text+=str(i)+"\n"
        if text:
            print(text.strip())
            sendmail(text.strip())
        else:
            print(0)