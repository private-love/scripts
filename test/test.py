#encoding: utf-8
import socket
import multiprocessing
import time
from multiprocessing import Pool
#iplist = ["192.168.0.238","192.168.0.65","192.168.0.14","192.168.0.65","192.168.3.217"]
#print(sorted(iplist, key=socket.inet_aton))
#iplist = list(set(iplist))
#print(sorted(iplist, key=socket.inet_aton))
#del iplist[0:3]
#iplist = iplist[-3:]
#print(iplist)
#from sendhtml import sendmail
#width=\"600\"
def start(i):
    print("start")
    time.sleep(5)
    print("end")
    return i
def check():
    p = Pool(5)
    list = [1, 2, 3, 4, 5]
    Pool.
    result = p.map(start, list)
    p.close()
    p.join()
    return result
print(check())