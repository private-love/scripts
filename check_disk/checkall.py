# -*- coding: utf-8 -*-
import paramiko, re , iplist
import multiprocessing
import math, sendhtml
def convertKB(bytes,lst=['KB', 'MB', 'GB', 'TB', 'PB']):
    i = int(math.floor(math.log(bytes, 1024)))
    if i >= len(lst):
        i = len(lst) - 1
    return ('%.2f' + " " + lst[i]) % (bytes/math.pow(1024, i))
def sshcommend(ipnum,portnum,sship="",sshport=""):
    private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/k8sroot_key')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ipnum, port=int(portnum), username='root', pkey=private_key)
    if not sship:
        commend = "df -T|grep -Ev 'nfs|tmpfs|overlay|Filesystem|boot'|grep '/'|grep '%'|awk '{if ($(NF-2) <= 52428800 && $(NF-1) >= \"95%\") print $NF,$(NF-1),$(NF-2)}'"
    else:
        commend = "ssh " + sship + " -p " + sshport + \
                  " df -T|grep -Ev 'nfs|tmpfs|overlay|Filesystem|boot'|grep '/'|grep '%'|awk '{if ($(NF-2) <= 52428800 && $(NF-1) >= \"95%\") print $NF,$(NF-1),$(NF-2)}'"
    stdin, stdout, stderr = ssh.exec_command(commend)
    result=stdout.read()
#    print(result.strip())
    return result.strip()
    ssh.close()
def sshpasswd(ipnum, portnum, wd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ipnum, port=portnum, username='root', password=wd)
    stdin, stdout, stderr = ssh.exec_command('sh /root/jr/check_mac.sh > /dev/null 2>&1')
    ssh.close()
    print(ipnum + '\033[0;32m  success\033[0m')
def dicttohtml(dict):
    html = "<head><style>td {text-align:center}</style><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head>" \
           "<table width=\"400\" border=\"1\" cellspacing=\"0\" cellpadding=\"2\">"
    html += "<tr style=\"text-align:center;\"><td>IP</td><td style=\"text-align:center;\">目录</td><td>已用比例</td><td>剩余大小</td></tr><tr>"
    for key in dict:
        values = dict[key].split("\n")
        value_len=len(values)
        html += "<td rowspan=" + str(value_len) + ">" + key + "</td>"
        for value in values:
            html += "<td>" + value.split()[0] + "</td><td>" + value.split()[1] + "</td><td>" + str(convertKB(int(value.split()[2]))) + "</td></tr><tr>"
    html += "</tr></table>"
    return html
def check():
    f = open('./iplist.txt', 'r')
    ipdict={}
    for ips in f:
        ip = ips.strip()
        if not ip.startswith ('#'):
            b = re.split(r":|-", ip)
            if len(b) > 3:
                ipdict[b[0]+":"+b[1]] = b[2]+":"+b[3]
            else:
                ipdict[b[0]+":"+b[1]] = ""
    pronum = len(ipdict)
    p = multiprocessing.Pool(processes=pronum)
    text={}
    for key in ipdict:
        send = key.split(":");sshsend = ipdict[key].split(":")
        print(send[0] + "start")
        if ipdict[key]:
            resultget = p.apply_async(sshcommend, args=(sshsend[0], sshsend[1], send[0], send[1]))
        else:
            resultget=p.apply_async(sshcommend, args=(send[0], send[1],))
        result = resultget.get()
        if result:
            text[send[0]]=result
        print(send[0] + "end")
    p.close()
    p.join()
#    sorted_text = sorted(text.items(), key = lambda text:text[0], reverse = False)
    sorted_text = sorted(text.items(), key=lambda text: (int(text[0].split('.')[0]), int(text[0].split('.')[1]), int(text[0].split('.')[2]), int(text[0].split('.')[3])))
#    print(sorted_text)
    return dict(sorted_text)
def dictcheck():
    iplist_dict = iplist.iplist_dict
    print(iplist_dict)
    text = {}
    p = multiprocessing.Pool(processes=4)
    for key in iplist_dict:
        for value in iplist_dict[key]:
            value_l = value.split(":")
            key_l = key.split(":")
            print(value_l[0] + " start")
            if key == "publicnetwork":
                resultget = p.apply_async(sshcommend, args=(value_l[0], value_l[1],))
            else:
                resultget = p.apply_async(sshcommend, args=(key_l[0], key_l[1], value_l[0], value_l[1]))
            result = (resultget.get())
            if result:
                text[value_l[0]] = result
        print(value_l[0] + " end")
    p.close()
    p.join()
    return text
if __name__ == '__main__':
    text = dictcheck()
    print(text)
    if text:
        html=dicttohtml(text)
#        print(html)
#        sendhtml.sendmail(html)
    else:
        print("none")