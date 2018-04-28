#-*- coding: utf-8 -*- 
import paramiko,re,sys,time
import multiprocessing
def sshcommend(ipnum,portnum):
    private_key = paramiko.RSAKey.from_private_key_file('/home/wlx/.ssh/k8sroot_key')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ipnum, port=int(portnum), username='root', pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command('python /root/check_mac.py > /dev/null 2>&1')
    result=stdout.read()
    ssh.close()
    print(ipnum + '\033[0;32m  success\033[0m')
def sshpasswd(ipnum,portnum,wd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ipnum, port=portnum, username='root', password=wd)
    stdin, stdout, stderr = ssh.exec_command('sh /root/jr/check_mac.sh > /dev/null 2>&1')
    ssh.close()
    print(ipnum + '\033[0;32m  success\033[0m')
def checkmac():
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
    for i in range(len(iplist)):
        p.apply_async(sshcommend,args=(iplist[i],portlist[i],))
    p.close()
    p.join()
if __name__ == '__main__':
    checkmac()
    sshpasswd('192.168.2.240',22,'ci123vm')
