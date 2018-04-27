#-*- coding: utf-8 -*- 
import paramiko,re,sys,time
import multiprocessing
def sshcommend(ipnum,portnum):
    private_key = paramiko.RSAKey.from_private_key_file('/home/wlx/.ssh/k8sroot_key')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ipnum, port=int(portnum), username='root', pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command('python /root/common_scripts/ziplog.py')
    result=stdout.read()
    ssh.close()
    print(sys.stdout.write(result))
def rsyncfile(ipnum,portnum):
    private_key = paramiko.RSAKey.from_private_key_file('/home/wlx/.ssh/k8sroot_key')
    transport = paramiko.Transport((ipnum,int(portnum)))
    transport.connect(username='root', pkey=private_key )
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put('./ziplog.py', '/root/common_scripts/ziplog.py')
    transport.close()
    print('copy file to '+ipnum)
    time.sleep(30)
def cpfile():
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
        p.apply_async(rsyncfile,args=(iplist[i],portlist[i],))
    p.close()
    p.join()
def zipfile():
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
    cpfile()
#    zipfile()
