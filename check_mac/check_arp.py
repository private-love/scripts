# coding: utf-8
import os
from multiprocessing import Pool
def check(i):
    ip = "192.168.0." + str(i)
    command = "arping -I em1 -c 2 -w 2 " + ip + "|grep Unicast|awk '{print $5}'|awk -F '[' '{print $2}'|awk -F ']' '{print $1}'"
    arp = os.popen(command)
    arp = arp.read().strip()
    arplist = arp.split("\n")
    print(arplist)
    arpdict = {ip:arplist}
    return arpdict
def start():
    list = [x for x in range(2, 254)]
    p = Pool(100)
    print(list)
    data = p.map(check, list)
    p.close()
    p.join()
    print(data)
    dictall = {}
    for ip in data:
        for key in ip:
            if ip[key] != ['']:
                if ip[key][0] != ip[key][1]:
                    dictall[key] = ip[key]
    print(dictall)
    return dictall
if __name__ == '__main__':
    start()